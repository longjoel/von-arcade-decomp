#!/usr/bin/env python3
"""Contract tests for bounded capture sidecar manifests."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from capture_manifest import directory_sha256, entry, validate
from normalize_mame_trace import load_provenance


TOOL = Path(__file__).resolve().parent / "capture_manifest.py"


def main() -> int:
    assert any("capture manifest must be an object" in error for error in validate([], Path.cwd()))
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for name in ("cfg", "nvram", "state"):
            (root / name).mkdir()
        input_path = root / "rom-manifest.json"
        artifact_path = root / "events.ndjson"
        input_path.write_text('{"rom": "fixture"}\n', encoding="utf-8")
        artifact_path.write_text('{"seq": 1}\n', encoding="utf-8")
        report_path = root / "coverage.json"
        report_path.write_text('{"capture_id": "fixture-v1", "tier": "A", "edge_semantics": "possible_static_edges", "canonical": false, "registration": "discovery-only", "phase": "stable-attract"}\n', encoding="utf-8")
        manifest = {
            "schema_version": 1, "id": "fixture-v1", "objective": "test-capture",
            "hypothesis": "coverage is bounded", "expected_discriminator": "report is Tier A",
            "stimulus": {"kind": "input-free-attract", "seconds": 1, "phase": "stable-attract"},
            "checkpoints": ["reset", "scheduler"],
            "configuration": {"set": "vonj", "mame_revision": "a" * 40,
                               "patch_profile": "none", "execution_engine": "interpreter"},
            "command": ["mame", "vonj", "-video", "none",
                         "-cfg_directory", str(root / "cfg"),
                         "-nvram_directory", str(root / "nvram"),
                         "-state_directory", str(root / "state"),
                         "-seconds_to_run", "1"],
            "isolation": {"cfg_directory": "cfg", "nvram_directory": "nvram", "state_directory": "state"},
            "inputs": [entry(input_path, root)],
            "artifacts": [entry(artifact_path, root), entry(report_path, root)],
            "coverage_report": "coverage.json",
        }
        for field in ("cfg_directory", "nvram_directory", "state_directory"):
            manifest["isolation"][f"{field}_sha256"] = directory_sha256(root / manifest["isolation"][field])
        assert not validate(manifest, root)
        relative_command_manifest = copy.deepcopy(manifest)
        for flag, directory in (("-cfg_directory", "cfg"), ("-nvram_directory", "nvram"),
                                 ("-state_directory", "state")):
            index = relative_command_manifest["command"].index(flag)
            relative_command_manifest["command"][index + 1] = directory
        assert not validate(relative_command_manifest, root)
        manifest_path = root / "capture.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        provenance = load_provenance(manifest_path, root, artifact_path)
        assert provenance["capture_id"] == "fixture-v1"
        assert provenance["artifact_sha256"] == manifest["artifacts"][0]["sha256"]
        linked_trace = root / "linked-events.ndjson"
        linked_trace.symlink_to(artifact_path)
        try:
            load_provenance(manifest_path, root, linked_trace)
        except ValueError as error:
            assert "must not be a symlink" in str(error)
        else:
            raise AssertionError("symlinked trace provenance was accepted")
        linked_manifest = root / "linked-capture.json"
        linked_manifest.symlink_to(manifest_path)
        try:
            load_provenance(linked_manifest, root, artifact_path)
        except ValueError as error:
            assert "manifest must not be a symlink" in str(error)
        else:
            raise AssertionError("symlinked capture provenance was accepted")
        outside_manifest = root.parent / "outside-capture.json"
        outside_manifest.write_text(manifest_path.read_text(encoding="utf-8"), encoding="utf-8")
        try:
            load_provenance(outside_manifest, root, artifact_path)
        except ValueError as error:
            assert "escapes capture root" in str(error)
        else:
            raise AssertionError("external capture provenance was accepted")
        try:
            load_provenance(manifest_path, root, root / "unlisted.ndjson")
        except ValueError as error:
            assert "not declared" in str(error)
        else:
            raise AssertionError("undeclared trace artifact was accepted")
        broken = copy.deepcopy(manifest)
        broken["artifacts"][0]["sha256"] = "0" * 64
        assert any("hash mismatch" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["artifacts"][0]["sha256"] = "invalid"
        assert any("must be a SHA-256" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["command"] = []
        assert any("command" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["command"][broken["command"].index("-seconds_to_run") + 1] = "2"
        assert any("seconds_to_run" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["command"].extend(["-seconds_to_run", "1"])
        assert any("only once" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["command"][broken["command"].index("-cfg_directory") + 1] = str(root / "nvram")
        assert any("does not match isolation.cfg_directory" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["command"].extend(["-cfg_directory", str(root / "cfg")])
        assert any("contain -cfg_directory only once" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["stimulus"]["phase"] = "startup"
        assert any("phase" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["coverage_report"] = "coverage.json"
        report_path.write_text('{"capture_id": "other", "tier": "A"}\n', encoding="utf-8")
        assert any("capture_id" in error for error in validate(broken, root))
        report_path.write_text('[]\n', encoding="utf-8")
        assert any("coverage report must be an object" in error for error in validate(manifest, root))
        report_path.write_text('{"capture_id": "fixture-v1", "tier": "A", "edge_semantics": "executed_edges"}\n', encoding="utf-8")
        assert any("possible_static_edges" in error for error in validate(manifest, root))
        report_path.write_text('{"capture_id": "fixture-v1", "tier": "A", "edge_semantics": "possible_static_edges", "canonical": false, "registration": "discovery-only", "phase": "stable-attract"}\n', encoding="utf-8")
        report_path.write_text('{"capture_id": "fixture-v1", "tier": "A", "edge_semantics": "possible_static_edges", "canonical": true, "registration": "canonical", "phase": "stable-attract"}\n', encoding="utf-8")
        assert any("explicitly noncanonical" in error for error in validate(manifest, root))
        report_path.write_text('{"capture_id": "fixture-v1", "tier": "A", "edge_semantics": "possible_static_edges", "canonical": false, "registration": "discovery-only", "phase": "stable-attract"}\n', encoding="utf-8")
        broken = copy.deepcopy(manifest)
        broken["artifacts"][0]["path"] = "../outside.log"
        assert any("missing file" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["artifacts"] = []
        assert any("at least one artifact" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["artifacts"] = [entry(artifact_path, root)]
        assert any("coverage report must be a declared" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken.pop("coverage_report")
        assert any("requires coverage_report" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["objective"] = ""
        assert any("objective" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["id"] = "captures/capture.json"
        assert any("stable capture id" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["checkpoints"] = ["reset", "reset"]
        assert any("checkpoints" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken.pop("checkpoints")
        assert any("checkpoints" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["stimulus"]["seconds"] = -1
        assert any("numeric seconds" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["stimulus"]["seconds"] = float("inf")
        assert any("numeric seconds" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["artifacts"] = ["malformed"]
        assert any("must be an object" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["inputs"] = {"path": "rom-manifest.json"}
        assert any("inputs must be an array" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["inputs"] = []
        assert any("runtime capture requires at least one hashed input" in error
                   for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        del broken["inputs"]
        assert any("inputs must be an array" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["artifacts"].append(copy.deepcopy(broken["artifacts"][0]))
        assert any("duplicate file" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["inputs"] = [entry(artifact_path, root)]
        assert any("multiple sections" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["isolation"]["nvram_directory"] = "cfg"
        broken["isolation"]["nvram_directory_sha256"] = broken["isolation"]["cfg_directory_sha256"]
        assert any("directories must be distinct" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["configuration"] = []
        assert any("configuration must be an object" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["configuration"]["mame_revision"] = ["abc"]
        assert any("configuration.mame_revision must be a non-empty string" in error
                   for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["configuration"]["mame_revision"] = "abc"
        assert any("configuration.mame_revision must be a 40-hex commit" in error
                   for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["command"][1] = "other-set"
        assert any("command set does not match configuration.set" in error
                   for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        del broken["stimulus"]["phase"]
        assert any("runtime capture requires a non-empty stimulus.phase" in error
                   for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["isolation"] = []
        assert any("isolation must be an object" in error for error in validate(broken, root))
        outside = root.parent / "outside-capture-fixture.txt"
        outside.write_text("outside\n", encoding="utf-8")
        link = root / "linked-artifact.txt"
        link.symlink_to(outside)
        broken = copy.deepcopy(manifest)
        broken["artifacts"] = [{"path": "linked-artifact.txt", "sha256": ""}]
        assert any("missing file" in error for error in validate(broken, root))
        loop_artifact = root / "loop-artifact.txt"
        loop_artifact.symlink_to(loop_artifact)
        broken = copy.deepcopy(manifest)
        broken["artifacts"] = [{"path": "loop-artifact.txt", "sha256": ""}]
        assert any("missing file" in error for error in validate(broken, root))
        local_link = root / "local-link-artifact.txt"
        local_link.symlink_to(artifact_path)
        broken = copy.deepcopy(manifest)
        broken["artifacts"] = [{"path": "local-link-artifact.txt", "sha256": "0" * 64}]
        assert any("missing file" in error for error in validate(broken, root))
        linked_artifact_directory = root / "linked-artifacts"
        linked_artifact_directory.symlink_to(root)
        broken = copy.deepcopy(manifest)
        broken["artifacts"] = [{"path": "linked-artifacts/events.ndjson", "sha256": "0" * 64}]
        assert any("missing file" in error for error in validate(broken, root))
        isolation_link = root / "cfg" / "linked-outside.txt"
        isolation_link.symlink_to(outside)
        broken = copy.deepcopy(manifest)
        assert any("invalid isolation.cfg_directory" in error for error in validate(broken, root))
        isolation_link.unlink()
        isolation_loop = root / "cfg" / "loop"
        isolation_loop.symlink_to(isolation_loop)
        assert any("invalid isolation.cfg_directory" in error for error in validate(manifest, root))
        isolation_loop.unlink()
        isolation_directory_link = root / "linked-cfg-directory"
        isolation_directory_link.symlink_to(root / "cfg", target_is_directory=True)
        broken = copy.deepcopy(manifest)
        broken["isolation"]["cfg_directory"] = "linked-cfg-directory"
        assert any("missing isolation directory" in error
                   for error in validate(broken, root))
        causal = copy.deepcopy(manifest)
        causal["stimulus"]["kind"] = "causal-trace"
        causal.pop("coverage_report")
        assert not validate(causal, root)
        linked_output = root / "linked-output.json"
        linked_output.symlink_to(manifest_path)
        cli_result = subprocess.run(
            [sys.executable, str(TOOL), "--output", str(linked_output), "--root", str(root),
             "--id", "cli-v1", "--objective", "objective", "--hypothesis", "hypothesis",
             "--expected-discriminator", "discriminator", "--seconds", "1",
             "--checkpoint", "reset", "--set", "fixture", "--mame-revision", "abc",
             "--patch-profile", "none", "--execution-engine", "interpreter",
             "--command", "mame", "--cfg-directory", str(root / "cfg"),
             "--nvram-directory", str(root / "nvram"), "--state-directory", str(root / "state")],
            cwd=root, capture_output=True, text=True, check=False,
        )
        assert cli_result.returncode == 1
        assert "output path must not contain symlink components" in cli_result.stdout
        linked_output_parent = root / "linked-output-parent"
        linked_output_parent.symlink_to(root, target_is_directory=True)
        cli_result = subprocess.run(
            [sys.executable, str(TOOL), "--output", str(linked_output_parent / "nested-output.json"),
             "--root", str(root), "--id", "cli-v1-parent", "--objective", "objective",
             "--hypothesis", "hypothesis", "--expected-discriminator", "discriminator",
             "--seconds", "1", "--checkpoint", "reset", "--set", "fixture",
             "--mame-revision", "abc", "--patch-profile", "none",
             "--execution-engine", "interpreter", "--command", "mame",
             "--cfg-directory", str(root / "cfg"), "--nvram-directory", str(root / "nvram"),
             "--state-directory", str(root / "state")],
            cwd=root, capture_output=True, text=True, check=False,
        )
        assert cli_result.returncode == 1
        assert "output path must not contain symlink components" in cli_result.stdout
        cli_result = subprocess.run(
            [sys.executable, str(TOOL), "--output", str(root / "outside-input.json"),
             "--root", str(root), "--id", "cli-v2", "--objective", "objective",
             "--hypothesis", "hypothesis", "--expected-discriminator", "discriminator",
             "--seconds", "1", "--checkpoint", "reset", "--set", "fixture",
             "--mame-revision", "abc", "--patch-profile", "none",
             "--execution-engine", "interpreter", "--command", "mame",
             "--cfg-directory", str(root / "cfg"), "--nvram-directory", str(root / "nvram"),
             "--state-directory", str(root / "state"), "--artifact", str(outside)],
            cwd=root, capture_output=True, text=True, check=False,
        )
        assert cli_result.returncode == 1
        assert "artifact path escapes root" in cli_result.stdout
        linked_artifact_parent = root / "linked-artifact-parent"
        linked_artifact_parent.symlink_to(root, target_is_directory=True)
        cli_result = subprocess.run(
            [sys.executable, str(TOOL), "--output", str(root / "cli-parent-artifact.json"),
             "--root", str(root), "--id", "cli-v3", "--objective", "objective",
             "--hypothesis", "hypothesis", "--expected-discriminator", "discriminator",
             "--seconds", "1", "--checkpoint", "reset", "--set", "fixture",
             "--mame-revision", "abc", "--patch-profile", "none",
             "--execution-engine", "interpreter", "--command", "mame",
             "--cfg-directory", str(root / "cfg"), "--nvram-directory", str(root / "nvram"),
             "--state-directory", str(root / "state"),
             "--artifact", str(linked_artifact_parent / artifact_path.name)],
            cwd=root, capture_output=True, text=True, check=False,
        )
        assert cli_result.returncode == 1
        assert "artifact path must not contain symlink components" in cli_result.stdout
    print("PASS: capture sidecar manifest hashes and provenance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
