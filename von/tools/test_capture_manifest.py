#!/usr/bin/env python3
"""Contract tests for bounded capture sidecar manifests."""

from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path

from capture_manifest import directory_sha256, entry, validate
from normalize_mame_trace import load_provenance


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
        report_path.write_text('{"capture_id": "fixture-v1", "tier": "A", "edge_semantics": "possible_static_edges", "phase": "stable-attract"}\n', encoding="utf-8")
        manifest = {
            "schema_version": 1, "id": "fixture-v1", "objective": "test-capture",
            "stimulus": {"kind": "input-free-attract", "seconds": 1, "phase": "stable-attract"},
            "configuration": {"set": "fixture", "mame_revision": "abc",
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
        manifest_path = root / "capture.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        provenance = load_provenance(manifest_path, root, artifact_path)
        assert provenance["capture_id"] == "fixture-v1"
        assert provenance["artifact_sha256"] == manifest["artifacts"][0]["sha256"]
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
        report_path.write_text('{"capture_id": "fixture-v1", "tier": "A", "edge_semantics": "executed_edges"}\n', encoding="utf-8")
        assert any("possible_static_edges" in error for error in validate(manifest, root))
        report_path.write_text('{"capture_id": "fixture-v1", "tier": "A", "edge_semantics": "possible_static_edges", "phase": "stable-attract"}\n', encoding="utf-8")
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
        broken["stimulus"]["seconds"] = -1
        assert any("numeric seconds" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["artifacts"] = ["malformed"]
        assert any("must be an object" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["inputs"] = {"path": "rom-manifest.json"}
        assert any("inputs must be an array" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["artifacts"].append(copy.deepcopy(broken["artifacts"][0]))
        assert any("duplicate file" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["isolation"]["nvram_directory"] = "cfg"
        broken["isolation"]["nvram_directory_sha256"] = broken["isolation"]["cfg_directory_sha256"]
        assert any("directories must be distinct" in error for error in validate(broken, root))
        broken = copy.deepcopy(manifest)
        broken["configuration"] = []
        assert any("configuration must be an object" in error for error in validate(broken, root))
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
        causal = copy.deepcopy(manifest)
        causal["stimulus"]["kind"] = "causal-trace"
        causal.pop("coverage_report")
        assert not validate(causal, root)
    print("PASS: capture sidecar manifest hashes and provenance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
