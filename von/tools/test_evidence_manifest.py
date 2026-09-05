#!/usr/bin/env python3
"""Contract test for the tracked evidence manifest."""

from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

from capture_manifest import directory_sha256, entry
from evidence_manifest import validate


TOOL = Path(__file__).resolve().parent / "evidence_manifest.py"


def main() -> int:
    root = Path.cwd()
    assert any("ledger must be an object" in error
               for error in validate({"schema_version": 1, "entries": []}, [], root))
    assert not any("Traceback" in error for error in validate(
        {"schema_version": 1, "entries": []},
        {"images": [{"work_units": {}}]}, root))
    manifest = json.loads((root / "von/evidence/manifest.json").read_text(encoding="utf-8"))
    ledger = json.loads((root / "von/reconstruction_ledger.json").read_text(encoding="utf-8"))
    assert not validate(manifest, ledger, root)
    broken = json.loads(json.dumps(manifest))
    broken["schema_version"] = 2
    assert any("schema_version" in error for error in validate(broken, ledger, root))
    broken = json.loads(json.dumps(manifest))
    broken["entries"][0]["canonical"] = "true"
    assert any("canonical must be boolean" in error for error in validate(broken, ledger, root))
    broken = json.loads(json.dumps(manifest))
    broken["entries"][0]["id"] = "von/build/capture.log"
    assert any("stable id must be a non-path string" in error
               for error in validate(broken, ledger, root))
    broken = json.loads(json.dumps(manifest))
    broken["entries"][0]["consumers"] = [""]
    assert any("must name existing ledger consumers" in error for error in validate(broken, ledger, root))
    broken = json.loads(json.dumps(manifest))
    broken["entries"][0]["outcome"] = "incomplete"
    assert any("outcome" in error for error in validate(broken, ledger, root))
    runtime = json.loads(json.dumps(manifest))
    runtime["entries"][0]["stimulus"] = {
        "kind": "input-free-attract", "description": "runtime fixture"
    }
    assert any("capture_manifest" in error for error in validate(runtime, ledger, root))
    broken = json.loads(json.dumps(manifest))
    broken["entries"][0]["verifier"] = "/tmp/verify.py"
    assert any("verifier" in error for error in validate(broken, ledger, root))
    broken = json.loads(json.dumps(manifest))
    broken["entries"][0]["verifier_sha256"] = "0" * 64
    assert any("verifier hash mismatch" in error for error in validate(broken, ledger, root))
    broken = json.loads(json.dumps(manifest))
    del broken["entries"][0]["verifier_sha256"]
    assert any("verifier_sha256 must be" in error for error in validate(broken, ledger, root))
    broken = json.loads(json.dumps(manifest))
    broken["entries"][0]["artifacts"][0]["path"] = "../outside.json"
    assert any("artifact path" in error for error in validate(broken, ledger, root))
    broken = json.loads(json.dumps(manifest))
    broken["entries"][0]["artifacts"][0]["sha256"] = "invalid"
    assert any("artifact sha256" in error for error in validate(broken, ledger, root))
    broken = json.loads(json.dumps(manifest))
    broken["entries"][0]["inputs"] = [{"path": "/tmp/private-rom-manifest.json", "sha256": "a" * 64}]
    assert any("invalid input path" in error for error in validate(broken, ledger, root))
    broken = json.loads(json.dumps(manifest))
    broken["entries"][0]["artifacts"] = broken["entries"][0]["artifacts"] * 2
    assert any("duplicate artifact" in error for error in validate(broken, ledger, root))
    broken = json.loads(json.dumps(manifest))
    broken["entries"][0]["inputs"] = [copy for copy in broken["entries"][0]["artifacts"]]
    assert any("multiple sections" in error for error in validate(broken, ledger, root))
    broken = json.loads(json.dumps(manifest))
    broken["entries"] = ["malformed"]
    assert any("entry must be an object" in error for error in validate(broken, ledger, root))
    broken = json.loads(json.dumps(manifest))
    broken["entries"][0]["consumers"] = ["maincpu.opcode-0b-vector-service"] * 2
    assert any("existing ledger consumers" in error for error in validate(broken, ledger, root))
    broken = json.loads(json.dumps(manifest))
    broken["entries"][0]["configuration"] = []
    assert any("configuration must be an object" in error for error in validate(broken, ledger, root))
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        for name in ("cfg", "nvram", "state"):
            (temp / name).mkdir()
        summary = temp / "summary.json"
        summary.write_text('{"capture_id":"capture-v1","tier":"A","edge_semantics":"possible_static_edges","canonical":false,"registration":"discovery-only"}\n', encoding="utf-8")
        input_path = temp / "rom-manifest.json"
        input_path.write_text('{"rom":"fixture"}\n', encoding="utf-8")
        verifier = temp / "verify.py"
        verifier.write_text("# verifier\n", encoding="utf-8")
        capture = {
            "schema_version": 1, "id": "capture-v1", "objective": "pilot",
            "hypothesis": "startup reaches scheduler", "expected_discriminator": "scheduler checkpoint",
            "stimulus": {"kind": "input-free-attract", "seconds": 1, "phase": "startup"},
            "checkpoints": ["reset", "scheduler"],
            "configuration": {"set": "vonj", "mame_revision": "a" * 40, "patch_profile": "none", "execution_engine": "interpreter"},
            "command": ["mame", "vonj", "-cfg_directory", str(temp / "cfg"),
                         "-nvram_directory", str(temp / "nvram"),
                         "-state_directory", str(temp / "state"),
                         "-seconds_to_run", "1"],
            "isolation": {"cfg_directory": "cfg", "nvram_directory": "nvram", "state_directory": "state"},
            "coverage_report": "summary.json", "inputs": [entry(input_path, temp)], "artifacts": [entry(summary, temp)],
        }
        for field in ("cfg_directory", "nvram_directory", "state_directory"):
            capture["isolation"][f"{field}_sha256"] = directory_sha256(temp / capture["isolation"][field])
        (temp / "capture.json").write_text(json.dumps(capture), encoding="utf-8")
        runtime = {
            "schema_version": 1,
            "entries": [{"id": "capture-v1", "canonical": True,
                         "stimulus": {"kind": "input-free-attract", "description": "pilot",
                                      "seconds": 1, "phase": "startup"},
                         "checkpoints": capture["checkpoints"],
                         "hypothesis": capture["hypothesis"],
                         "expected_discriminator": capture["expected_discriminator"],
                         "configuration": capture["configuration"], "inputs": capture["inputs"],
                         "artifacts": capture["artifacts"],
                         "capture_manifest": "capture.json",
                         "capture_manifest_sha256": hashlib.sha256(
                             (temp / "capture.json").read_bytes()).hexdigest(),
                         "verifier": "verify.py",
                         "verifier_sha256": hashlib.sha256(
                             (temp / "verify.py").read_bytes()).hexdigest(),
                         "outcome": "pass", "consumers": ["unit"]}],
        }
        assert not validate(runtime, {"images": [{"work_units": [{"id": "unit"}]}]}, temp)
        missing_set = json.loads(json.dumps(runtime))
        del missing_set["entries"][0]["configuration"]["set"]
        assert any("configuration.set" in error for error in validate(
            missing_set, {"images": [{"work_units": [{"id": "unit"}]}]}, temp))
        outside = temp.parent / "outside-evidence-fixture.json"
        outside.write_text("{}\n", encoding="utf-8")
        (temp / "linked-capture.json").symlink_to(outside)
        escaped = json.loads(json.dumps(runtime))
        escaped["entries"][0]["capture_manifest"] = "linked-capture.json"
        assert any("missing capture manifest" in error for error in validate(
            escaped, {"images": [{"work_units": [{"id": "unit"}]}]}, temp))
        linked_local_capture = temp / "linked-local-capture.json"
        linked_local_capture.symlink_to(temp / "capture.json")
        linked_runtime = json.loads(json.dumps(runtime))
        linked_runtime["entries"][0]["capture_manifest"] = "linked-local-capture.json"
        assert any("missing capture manifest" in error for error in validate(
            linked_runtime, {"images": [{"work_units": [{"id": "unit"}]}]}, temp))
        loop_artifact = temp / "loop-artifact.json"
        loop_artifact.symlink_to(loop_artifact)
        looped = json.loads(json.dumps(runtime))
        looped["entries"][0]["artifacts"] = [{"path": "loop-artifact.json", "sha256": "0" * 64}]
        assert any("missing artifact" in error or "invalid artifact path" in error
                   for error in validate(looped, {"images": [{"work_units": [{"id": "unit"}]}]}, temp))
        local_link = temp / "local-link-summary.json"
        local_link.symlink_to(summary)
        linked_artifact = json.loads(json.dumps(runtime))
        linked_artifact["entries"][0]["artifacts"] = [{"path": "local-link-summary.json", "sha256": "0" * 64}]
        assert any("missing artifact" in error or "invalid artifact path" in error for error in validate(
            linked_artifact, {"images": [{"work_units": [{"id": "unit"}]}]}, temp))
        linked_directory = temp / "linked-evidence"
        linked_directory.symlink_to(temp)
        nested_artifact = json.loads(json.dumps(runtime))
        nested_artifact["entries"][0]["artifacts"] = [{"path": "linked-evidence/summary.json",
                                                         "sha256": "0" * 64}]
        assert any("missing artifact" in error or "invalid artifact path" in error
                   for error in validate(nested_artifact,
                                         {"images": [{"work_units": [{"id": "unit"}]}]}, temp))
        mismatched = json.loads(json.dumps(runtime))
        mismatched["entries"][0]["stimulus"]["kind"] = "causal-trace"
        assert any("stimulus kind" in error for error in validate(
            mismatched, {"images": [{"work_units": [{"id": "unit"}]}]}, temp))
        mismatched = json.loads(json.dumps(runtime))
        mismatched["entries"][0]["configuration"]["patch_profile"] = "stale"
        assert any("configuration.patch_profile" in error for error in validate(
            mismatched, {"images": [{"work_units": [{"id": "unit"}]}]}, temp))
        mismatched = json.loads(json.dumps(runtime))
        mismatched["entries"][0]["checkpoints"] = ["reset"]
        assert any("checkpoints" in error for error in validate(
            mismatched, {"images": [{"work_units": [{"id": "unit"}]}]}, temp))
        mismatched = json.loads(json.dumps(runtime))
        mismatched["entries"][0]["stimulus"]["phase"] = "stable-attract"
        assert any("stimulus phase" in error for error in validate(
            mismatched, {"images": [{"work_units": [{"id": "unit"}]}]}, temp))
        mismatched = json.loads(json.dumps(runtime))
        mismatched["entries"][0]["hypothesis"] = "different"
        assert any("hypothesis" in error for error in validate(
            mismatched, {"images": [{"work_units": [{"id": "unit"}]}]}, temp))
        mismatched = json.loads(json.dumps(runtime))
        mismatched["entries"][0]["artifacts"] = []
        assert any("artifacts do not match" in error for error in validate(
            mismatched, {"images": [{"work_units": [{"id": "unit"}]}]}, temp))
        capture["id"] = "other"
        (temp / "capture.json").write_text(json.dumps(capture), encoding="utf-8")
        assert any("does not match evidence id" in error for error in validate(runtime, {"images": [{"work_units": [{"id": "unit"}]}]}, temp))
        stale_hash = json.loads(json.dumps(runtime))
        stale_hash["entries"][0]["capture_manifest_sha256"] = "0" * 64
        assert any("capture manifest hash mismatch" in error for error in validate(
            stale_hash, {"images": [{"work_units": [{"id": "unit"}]}]}, temp))
    with tempfile.TemporaryDirectory(dir=root) as directory:
        temp = Path(directory)
        linked_manifest = temp / "linked-manifest.json"
        linked_manifest.symlink_to(root / "von/evidence/manifest.json")
        cli_result = subprocess.run(
            [sys.executable, str(TOOL), "--manifest", str(linked_manifest),
             "--ledger", str(root / "von/reconstruction_ledger.json")],
            cwd=root, capture_output=True, text=True, check=False,
        )
        assert cli_result.returncode == 1
        assert "manifest path must not be a symlink" in cli_result.stdout
        malformed_ledger = temp / "malformed-ledger.json"
        malformed_ledger.write_text("{invalid\n", encoding="utf-8")
        cli_result = subprocess.run(
            [sys.executable, str(TOOL), "--manifest", str(root / "von/evidence/manifest.json"),
             "--ledger", str(malformed_ledger)],
            cwd=root, capture_output=True, text=True, check=False,
        )
        assert cli_result.returncode == 1
        assert "unable to read validation document" in cli_result.stdout
    print("PASS: canonical evidence manifest contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
