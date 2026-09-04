#!/usr/bin/env python3
"""Contract test for the tracked evidence manifest."""

from __future__ import annotations

import json
import hashlib
import tempfile
from pathlib import Path

from capture_manifest import directory_sha256, entry
from evidence_manifest import validate


def main() -> int:
    root = Path.cwd()
    manifest = json.loads((root / "von/evidence/manifest.json").read_text(encoding="utf-8"))
    ledger = json.loads((root / "von/reconstruction_ledger.json").read_text(encoding="utf-8"))
    assert not validate(manifest, ledger, root)
    broken = json.loads(json.dumps(manifest))
    broken["schema_version"] = 2
    assert any("schema_version" in error for error in validate(broken, ledger, root))
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
        summary.write_text('{"capture_id":"capture-v1","tier":"A","edge_semantics":"possible_static_edges"}\n', encoding="utf-8")
        verifier = temp / "verify.py"
        verifier.write_text("# verifier\n", encoding="utf-8")
        capture = {
            "schema_version": 1, "id": "capture-v1", "objective": "pilot",
            "hypothesis": "startup reaches scheduler", "expected_discriminator": "scheduler checkpoint",
            "stimulus": {"kind": "input-free-attract", "seconds": 1},
            "checkpoints": ["reset", "scheduler"],
            "configuration": {"set": "vonj", "mame_revision": "abc", "patch_profile": "none", "execution_engine": "interpreter"},
            "command": ["mame", "vonj", "-cfg_directory", str(temp / "cfg"),
                         "-nvram_directory", str(temp / "nvram"),
                         "-state_directory", str(temp / "state"),
                         "-seconds_to_run", "1"],
            "isolation": {"cfg_directory": "cfg", "nvram_directory": "nvram", "state_directory": "state"},
            "coverage_report": "summary.json", "inputs": [], "artifacts": [entry(summary, temp)],
        }
        for field in ("cfg_directory", "nvram_directory", "state_directory"):
            capture["isolation"][f"{field}_sha256"] = directory_sha256(temp / capture["isolation"][field])
        (temp / "capture.json").write_text(json.dumps(capture), encoding="utf-8")
        runtime = {
            "schema_version": 1,
            "entries": [{"id": "capture-v1", "canonical": True,
                         "stimulus": {"kind": "input-free-attract", "description": "pilot"},
                         "checkpoints": capture["checkpoints"],
                         "hypothesis": capture["hypothesis"],
                         "expected_discriminator": capture["expected_discriminator"],
                         "configuration": capture["configuration"], "artifacts": capture["artifacts"],
                         "capture_manifest": "capture.json",
                         "capture_manifest_sha256": hashlib.sha256(
                             (temp / "capture.json").read_bytes()).hexdigest(),
                         "verifier": "verify.py",
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
    print("PASS: canonical evidence manifest contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
