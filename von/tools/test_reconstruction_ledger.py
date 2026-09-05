#!/usr/bin/env python3
"""Tests for schema-v2 migration, validation, and non-duplicated coverage."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from migrate_reconstruction_ledger import migrate
from reconstruction_ledger import code_coverage, validate, validate_lifecycle


TOOL = Path(__file__).resolve().parent / "validate_reconstruction_ledger.py"


def main() -> int:
    assert any("ledger must be an object" in error
               for error in validate([], Path.cwd()))
    assert any("images must be an array" in error
               for error in validate({"schema_version": 2, "images": {}}, Path.cwd()))
    assert any("ledger must be an object" in error
               for error in validate_lifecycle([], {"entries": []}))
    assert any("evidence manifest must be an object" in error
               for error in validate_lifecycle({"images": []}, []))
    assert any("evidence manifest entries must be an array" in error
               for error in validate_lifecycle({"images": []}, {}))
    assert any("manifest.entries[0]: entry must be an object" in error
               for error in validate_lifecycle({"images": []}, {"entries": ["bad"]}))
    assert any("stable id must be a non-empty string" in error
               for error in validate_lifecycle({"images": []}, {"entries": [{}]}))
    malformed_shape = {"schema_version": 2, "images": [{"name": "maincpu", "work_units": {}}]}
    assert any("work_units must be an array" in error for error in validate(malformed_shape))
    malformed_shape["images"][0]["work_units"] = [{"id": "unit", "classification": "code",
                                                     "stage": "planned", "sources": [], "ranges": {}}]
    assert any("ranges must be an array" in error for error in validate(malformed_shape))
    malformed_shape["images"][0]["work_units"][0]["ranges"] = []
    malformed_shape["images"][0]["work_units"][0]["evidence"] = "capture-v1"
    assert any("evidence must be a string array" in error for error in validate(malformed_shape))
    malformed_shape["images"][0]["work_units"][0]["evidence"] = [""]
    assert any("evidence must be a string array" in error for error in validate(malformed_shape))
    old = {"schema_version": 1, "images": [{"name": "maincpu", "size": 256, "slices": [
        {"name": "outer", "start": "0x10", "end": "0x30", "classification": "code", "status": "provisional", "source": "notes.md", "evidence": []},
        {"name": "inner", "start": "0x18", "end": "0x20", "classification": "code", "status": "provisional", "source": "model.c", "evidence": ["von/i960/recovered_example.c"]},
        {"name": "contract", "classification": "behavior", "status": "provisional", "source": "contract.md", "evidence": []},
    ]}]}
    ledger = migrate(old)
    assert not validate(ledger)
    assert code_coverage(ledger)["total"] == 0x20
    assert ledger["images"][0]["work_units"][1]["stage"] == "modeled"
    assert ledger["images"][0]["work_units"][1]["sources"] == ["model.c"]
    assert ledger["images"][0]["work_units"][1]["evidence"] == ["von/i960/recovered_example.c"]
    assert ledger["images"][0]["work_units"][2]["stage"] == "planned"
    assert "sources" in ledger["images"][0]["work_units"][0]
    broken = copy.deepcopy(ledger)
    broken["images"][0]["physical_ranges"].append({"id": "overlap", "start": "0x20", "end": "0x40", "classification": "code"})
    assert any("overlaps" in error for error in validate(broken))
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "roundtrip.json"
        path.write_text(json.dumps(ledger), encoding="utf-8")
        assert json.loads(path.read_text(encoding="utf-8"))["schema_version"] == 2
        linked_ledger = Path(directory) / "linked-ledger.json"
        linked_ledger.symlink_to(path)
        cli_result = subprocess.run(
            [sys.executable, str(TOOL), str(linked_ledger)],
            cwd=directory, capture_output=True, text=True, check=False,
        )
        assert cli_result.returncode == 1
        assert "ledger path must not be a symlink" in cli_result.stdout
        malformed_ledger = Path(directory) / "malformed-ledger.json"
        malformed_ledger.write_text("{invalid\n", encoding="utf-8")
        cli_result = subprocess.run(
            [sys.executable, str(TOOL), str(malformed_ledger)],
            cwd=directory, capture_output=True, text=True, check=False,
        )
        assert cli_result.returncode == 1
        assert "unable to read validation document" in cli_result.stdout
    lifecycle = {
        "schema_version": 2,
        "images": [{"name": "maincpu", "work_units": [
            {"id": "planned", "stage": "planned", "notes": "may matter"},
            {"id": "modeled", "stage": "modeled", "modeling": {
                "boundary": "MMIO inputs/outputs", "test": "test.py",
                "unresolved_behavior": "bus timing"
            }},
            {"id": "integrated", "stage": "integrated", "modeling": {
                "boundary": "RAM", "test": "test.py", "unresolved_behavior": "timing"
            }, "integration": {
                "image": "build/image.bin", "image_sha256": hashlib.sha256(b"image").hexdigest(),
                "checkpoint": "startup", "test": "test.py"
            }},
            {"id": "trace", "stage": "trace-validated", "modeling": {
                "boundary": "RAM", "test": "test.py", "unresolved_behavior": "timing"
            }, "integration": {
                "image": "build/image.bin", "image_sha256": hashlib.sha256(b"image").hexdigest(),
                "checkpoint": "startup", "test": "test.py"
            },
             "canonical_evidence_id": "capture-v1", "evidence": ["capture-v1"],
             "verifier": "verify.py",
             "verification": {"result": "pass"}},
            {"id": "bytes", "stage": "byte-validated", "modeling": {
                "boundary": "ROM", "test": "test.py", "unresolved_behavior": "none"
            }, "integration": {
                "image": "build/image.bin", "image_sha256": hashlib.sha256(b"image").hexdigest(),
                "checkpoint": "startup", "test": "test.py"
             }, "evidence": ["capture-v1"], "byte_validation": {
                "original_range": "0x100-0x110", "reconstructed_range": "0x20-0x30",
                "comparison": "match"
            }, "canonical_evidence_id": "capture-v1", "verifier": "verify.py",
             "verification": {"result": "pass"}},
            {"id": "blocked", "stage": "blocked", "blocked": {
                "missing_fact": "target", "failed_discriminator": "no event",
                "next_experiment": "capture call window"
            }},
        ]}],
    }
    manifest = {"entries": [{"id": "capture-v1", "canonical": True, "verifier": "verify.py", "outcome": "pass",
                              "verifier_sha256": "a" * 64,
                              "checkpoints": ["startup"], "consumers": ["trace", "bytes"]}]}
    assert not validate_lifecycle(lifecycle, manifest)
    with tempfile.TemporaryDirectory() as directory:
        lifecycle_root = Path(directory)
        (lifecycle_root / "build").mkdir()
        (lifecycle_root / "build/image.bin").write_bytes(b"image")
        (lifecycle_root / "test.py").write_text("# test\n", encoding="utf-8")
        (lifecycle_root / "verify.py").write_text("# verifier\n", encoding="utf-8")
        rooted_manifest = copy.deepcopy(manifest)
        rooted_manifest["entries"][0]["verifier_sha256"] = hashlib.sha256(
            (lifecycle_root / "verify.py").read_bytes()).hexdigest()
        assert not validate_lifecycle(lifecycle, rooted_manifest, lifecycle_root)
        linked_verifier = lifecycle_root / "verify-link.py"
        linked_verifier.symlink_to(lifecycle_root / "verify.py")
        linked_lifecycle = copy.deepcopy(lifecycle)
        linked_lifecycle["images"][0]["work_units"][3]["verifier"] = "verify-link.py"
        linked_manifest = copy.deepcopy(rooted_manifest)
        linked_manifest["entries"][0]["verifier"] = "verify-link.py"
        assert any("missing verifier" in error for error in validate_lifecycle(
            linked_lifecycle, linked_manifest, lifecycle_root))
        linked_directory = lifecycle_root / "linked-tools"
        linked_directory.symlink_to(lifecycle_root)
        nested_lifecycle = copy.deepcopy(lifecycle)
        nested_lifecycle["images"][0]["work_units"][3]["verifier"] = "linked-tools/verify.py"
        nested_manifest = copy.deepcopy(rooted_manifest)
        nested_manifest["entries"][0]["verifier"] = "linked-tools/verify.py"
        assert any("missing verifier" in error for error in validate_lifecycle(
            nested_lifecycle, nested_manifest, lifecycle_root))
        stale_manifest = copy.deepcopy(rooted_manifest)
        stale_manifest["entries"][0]["verifier_sha256"] = "0" * 64
        assert any("verifier hash mismatch" in error for error in validate_lifecycle(
            lifecycle, stale_manifest, lifecycle_root))
    broken = copy.deepcopy(lifecycle)
    broken["images"][0]["work_units"][1]["active"] = True
    broken["images"][0]["work_units"].append({
        "id": "another-modeled", "stage": "modeled", "active": True,
        "modeling": {"boundary": "RAM", "test": "test.py", "unresolved_behavior": "timing"},
    })
    assert any("work-in-progress limit" in error for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    broken["images"][0]["work_units"][2]["active"] = True
    assert any("active work-in-progress must be modeled" in error
               for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    broken["images"][0]["work_units"][1]["active"] = "true"
    assert any("active must be boolean" in error
               for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    broken["images"][0]["work_units"][1]["modeling"].pop("boundary")
    assert any("modeled requires modeling.boundary" in error for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    broken["images"][0]["work_units"][1]["modeling"]["boundary"] = ["RAM"]
    assert any("modeled requires modeling.boundary" in error for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    del broken["images"][0]["work_units"][2]["integration"]
    assert any("integrated requires" in error for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    del broken["images"][0]["work_units"][3]["modeling"]
    assert any("preceding modeling" in error for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    broken["images"][0]["work_units"][3]["integration"] = []
    assert any("requires preceding integration evidence" in error
               for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    broken["images"][0]["work_units"][3]["modeling"].pop("boundary")
    assert any("trace-validated requires modeling.boundary" in error
               for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    broken["images"][0]["work_units"][3]["integration"].pop("test")
    assert any("trace-validated requires integration.test" in error
               for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    broken["images"][0]["work_units"][3]["integration"]["checkpoint"] = "other"
    assert any("does not declare integration checkpoint" in error
               for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    del broken["images"][0]["work_units"][2]["integration"]["image"]
    assert any("integration.image" in error for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    broken["images"][0]["work_units"][2]["integration"]["image"] = "../outside.bin"
    assert any("safe relative path" in error for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    broken["images"][0]["work_units"][2]["integration"]["checkpoint"] = ["startup"]
    assert any("integration.checkpoint" in error for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    broken["images"][0]["work_units"][3]["canonical_evidence_id"] = "von/build/capture.log"
    assert any("canonical evidence id" in error for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    broken["images"][0]["work_units"][3]["verifier"] = "other.py"
    assert any("differs from canonical" in error for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    broken["images"][0]["work_units"][3]["id"] = "unregistered-consumer"
    assert any("does not name this unit" in error for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    broken["images"][0]["work_units"][3]["verification"]["result"] = "fail"
    assert any("verification.result=pass" in error for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    broken["images"][0]["work_units"][3]["verifier"] = "../verify.py"
    assert any("safe relative path" in error for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    broken["images"][0]["work_units"][1]["modeling"]["test"] = "../test.py"
    assert any("modeling.test must be a safe" in error for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    broken["images"][0]["work_units"][2]["integration"]["test"] = "../test.py"
    assert any("integration.test must be a safe" in error for error in validate_lifecycle(broken, manifest))
    missing_verifier = copy.deepcopy(manifest)
    del missing_verifier["entries"][0]["verifier"]
    assert any("differs from canonical" in error for error in validate_lifecycle(lifecycle, missing_verifier))
    missing_outcome = copy.deepcopy(manifest)
    del missing_outcome["entries"][0]["outcome"]
    assert any("outcome must be pass" in error for error in validate_lifecycle(lifecycle, missing_outcome))
    malformed_canonical = copy.deepcopy(manifest)
    malformed_canonical["entries"][0]["canonical"] = "true"
    assert any("canonical must be boolean" in error for error in validate_lifecycle(
        lifecycle, malformed_canonical))
    malformed_consumers = copy.deepcopy(manifest)
    malformed_consumers["entries"][0]["consumers"] = None
    assert any("canonical consumers must be a non-empty string array" in error
               for error in validate_lifecycle(lifecycle, malformed_consumers))
    unknown_consumers = copy.deepcopy(manifest)
    unknown_consumers["entries"][0]["consumers"] = ["missing-unit"]
    assert any("canonical consumers are unknown" in error
               for error in validate_lifecycle(lifecycle, unknown_consumers))
    broken = copy.deepcopy(lifecycle)
    broken["images"][0]["work_units"][3]["canonical_evidence_id"] = {}
    assert any("canonical evidence id" in error for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    broken["images"][0]["work_units"][3].pop("evidence")
    assert any("ledger evidence does not include canonical evidence id" in error
               for error in validate_lifecycle(broken, manifest))
    assert any("canonical evidence id" in error for error in validate_lifecycle(
        lifecycle, {"entries": ["malformed"]}))
    broken = copy.deepcopy(lifecycle)
    broken["images"][0]["work_units"][4]["byte_validation"]["comparison"] = "mismatch"
    assert any("must be match" in error for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    broken["images"][0]["work_units"][0]["stage"] = "finished"
    assert any("stage must be one of the known lifecycle stages" in error
               for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    broken["images"][0]["work_units"][4]["verifier"] = "../verify.py"
    assert any("safe relative path" in error for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    broken["images"][0]["work_units"][4]["verifier"] = "other.py"
    assert any("differs from canonical" in error for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    del broken["images"][0]["work_units"][4]["byte_validation"]["reconstructed_range"]
    assert any("reconstructed_range" in error for error in validate_lifecycle(broken, manifest))
    broken = copy.deepcopy(lifecycle)
    broken["images"][0]["work_units"][5]["blocked"]["next_experiment"] = {"command": "capture"}
    assert any("blocked requires" in error for error in validate_lifecycle(broken, manifest))
    bypass = copy.deepcopy(lifecycle)
    for field in ("canonical_evidence_id", "verifier", "verification"):
        bypass["images"][0]["work_units"][4].pop(field)
    assert any("byte-validated requires preceding canonical evidence" in error
               for error in validate_lifecycle(bypass, manifest))
    print("PASS: ledger v1 migration, schema-v2 validation, and union coverage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
