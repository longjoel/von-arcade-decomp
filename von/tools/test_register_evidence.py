#!/usr/bin/env python3
"""Contract tests for canonical evidence registration."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from capture_manifest import directory_sha256, entry
from register_evidence import register


TOOL = Path(__file__).resolve().parent / "register_evidence.py"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for name in ("cfg", "nvram", "state"):
            (root / name).mkdir()
        artifact = root / "summary.json"
        artifact.write_text('{"capture_id":"capture-v1","tier":"A","edge_semantics":"possible_static_edges"}\n', encoding="utf-8")
        input_path = root / "rom-manifest.json"
        input_path.write_text('{"rom":"fixture"}\n', encoding="utf-8")
        capture = {
            "schema_version": 1, "id": "capture-v1", "objective": "pilot",
            "hypothesis": "startup reaches scheduler", "expected_discriminator": "scheduler checkpoint",
            "stimulus": {"kind": "input-free-attract", "seconds": 1, "phase": "startup"},
            "checkpoints": ["reset", "scheduler"],
            "configuration": {"set": "vonj", "mame_revision": "a" * 40, "patch_profile": "none", "execution_engine": "interpreter"},
            "command": ["mame", "vonj", "-cfg_directory", str(root / "cfg"),
                         "-nvram_directory", str(root / "nvram"),
                         "-state_directory", str(root / "state"),
                         "-seconds_to_run", "1"],
            "isolation": {"cfg_directory": "cfg", "nvram_directory": "nvram", "state_directory": "state"},
            "coverage_report": "summary.json", "inputs": [entry(input_path, root)], "artifacts": [entry(artifact, root)],
        }
        for field in ("cfg_directory", "nvram_directory", "state_directory"):
            capture["isolation"][f"{field}_sha256"] = directory_sha256(root / capture["isolation"][field])
        verifier = root / "verify.py"
        verifier.write_text("# verifier\n", encoding="utf-8")
        capture_path = root / "capture.json"
        capture_path.write_text(json.dumps(capture) + "\n", encoding="utf-8")
        manifest = {"schema_version": 1, "entries": []}
        ledger = {"images": [{"work_units": [{"id": "unit-1"}]}]}
        assert "evidence manifest must be an object" in register([], capture, capture_path,
                                                               "bad", "verify.py", ["unit-1"], root, ledger)[0]
        assert "schema_version" in register({"schema_version": 2, "entries": []}, capture,
                                              capture_path, "bad", "verify.py", ["unit-1"], root, ledger)[0]
        assert "entries" in register({"schema_version": 1, "entries": {}}, capture,
                                       capture_path, "bad", "verify.py", ["unit-1"], root, ledger)[0]
        assert "stable id" in register({"schema_version": 1, "entries": [{}]}, capture,
                                         capture_path, "bad", "verify.py", ["unit-1"], root, ledger)[0]
        malformed_manifest = {"schema_version": 1, "entries": [{"id": "old", "canonical": "true"}]}
        assert "canonical must be boolean" in register(
            malformed_manifest, capture, capture_path, "bad", "verify.py", ["unit-1"], root, ledger)[0]
        assert malformed_manifest["entries"] == [{"id": "old", "canonical": "true"}]
        assert "duplicate evidence id" in register(
            {"schema_version": 1, "entries": [{"id": "old", "canonical": True},
                                                 {"id": "old", "canonical": True}]},
            capture, capture_path, "bad", "verify.py", ["unit-1"], root, ledger)[0]
        assert not register(manifest, capture, capture_path, "pilot capture", "verify.py", ["unit-1"], root, ledger)
        assert manifest["entries"][0]["canonical"] is True
        assert manifest["entries"][0]["capture_manifest"] == "capture.json"
        assert manifest["entries"][0]["checkpoints"] == capture["checkpoints"]
        assert manifest["entries"][0]["hypothesis"] == capture["hypothesis"]
        assert manifest["entries"][0]["capture_manifest_sha256"] == hashlib.sha256(
            capture_path.read_bytes()).hexdigest()
        assert manifest["entries"][0]["verifier_sha256"] == hashlib.sha256(
            verifier.read_bytes()).hexdigest()
        assert ledger["images"][0]["work_units"][0]["evidence"] == ["capture-v1"]
        mismatched_capture = copy.deepcopy(capture)
        mismatched_capture["objective"] = "different"
        assert any("differs from on-disk" in error for error in register(
            {"schema_version": 1, "entries": []}, mismatched_capture, capture_path,
            "mismatch", "verify.py", ["unit-1"], root))
        partially_invalid = {"images": [{"work_units": [
            {"id": "unit-1"}, {"id": "unit-2", "evidence": "invalid"}
        ]}]}
        before = copy.deepcopy(partially_invalid)
        assert any("invalid evidence list" in error for error in register(
            {"schema_version": 1, "entries": []}, capture, capture_path, "partial", "verify.py", ["unit-1", "unit-2"],
            root, partially_invalid))
        assert partially_invalid == before
        malformed_evidence = {"images": [{"work_units": [
            {"id": "unit-1", "evidence": [1]}
        ]}]}
        assert any("invalid evidence list" in error for error in register(
            {"schema_version": 1, "entries": []}, capture, capture_path, "malformed", "verify.py",
            ["unit-1"], root, malformed_evidence))
        assert any("consumers must be unique" in error for error in register(
            {"schema_version": 1, "entries": []}, capture, capture_path, "duplicate consumers", "verify.py",
            ["unit-1", "unit-1"], root, ledger))
        manifest_path = root / "manifest.json"
        ledger_path = root / "ledger.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
        linked_manifest = root / "linked-manifest.json"
        linked_manifest.symlink_to(manifest_path)
        cli_result = subprocess.run(
            [sys.executable, str(TOOL), "--manifest", str(linked_manifest),
             "--capture-manifest", str(capture_path), "--verifier", "verify.py",
             "--description", "description", "--consumer", "unit-1", "--root", str(root),
             "--ledger", str(ledger_path)],
            cwd=root, capture_output=True, text=True, check=False,
        )
        assert cli_result.returncode == 1
        assert "manifest path must not be a symlink" in cli_result.stdout
        linked_capture_cli = root / "linked-capture-cli.json"
        linked_capture_cli.symlink_to(capture_path)
        cli_result = subprocess.run(
            [sys.executable, str(TOOL), "--manifest", str(manifest_path),
             "--capture-manifest", str(linked_capture_cli), "--verifier", "verify.py",
             "--description", "description", "--consumer", "unit-1", "--root", str(root),
             "--ledger", str(ledger_path)],
            cwd=root, capture_output=True, text=True, check=False,
        )
        assert cli_result.returncode == 1
        assert "capture manifest path must not be a symlink" in cli_result.stdout
        outside_manifest = root.parent / "outside-evidence-manifest.json"
        outside_manifest.write_text(json.dumps(manifest), encoding="utf-8")
        cli_result = subprocess.run(
            [sys.executable, str(TOOL), "--manifest", str(outside_manifest),
             "--capture-manifest", str(capture_path), "--verifier", "verify.py",
             "--description", "description", "--consumer", "unit-1", "--root", str(root),
             "--ledger", str(ledger_path)],
            cwd=root, capture_output=True, text=True, check=False,
        )
        assert cli_result.returncode == 1
        assert "manifest path escapes root" in cli_result.stdout
        malformed_capture = root / "malformed-capture.json"
        malformed_capture.write_text("{invalid\n", encoding="utf-8")
        cli_result = subprocess.run(
            [sys.executable, str(TOOL), "--manifest", str(manifest_path),
             "--capture-manifest", str(malformed_capture), "--verifier", "verify.py",
             "--description", "description", "--consumer", "unit-1", "--root", str(root),
             "--ledger", str(ledger_path)],
            cwd=root, capture_output=True, text=True, check=False,
        )
        assert cli_result.returncode == 1
        assert "unable to read registration document" in cli_result.stdout
        assert any("non-empty string array" in error for error in register(
            {"schema_version": 1, "entries": []}, capture, capture_path, "scalar consumer", "verify.py",
            "unit-1", root, ledger))
        assert any("non-empty string array" in error for error in register(
            {"schema_version": 1, "entries": []}, capture, capture_path, "empty consumer", "verify.py",
            [""], root, ledger))
        assert any("ledger must be an object" in error for error in register(
            {"schema_version": 1, "entries": []}, capture, capture_path, "bad ledger", "verify.py",
            ["unit-1"], root, []))
        assert any("work_units must be an array" in error for error in register(
            {"schema_version": 1, "entries": []}, capture, capture_path, "bad units", "verify.py",
            ["unit-1"], root, {"images": [{"work_units": {}}]}))
        broken = copy.deepcopy(manifest)
        assert register(broken, capture, capture_path, "duplicate", "verify.py", ["unit-1"], root)
        assert "unknown ledger consumers" in register({"schema_version": 1, "entries": []}, capture, root / "capture.json", "unknown", "verify.py", ["missing"], root, ledger)[0]
        assert "missing verifier" in register({"schema_version": 1, "entries": []}, capture, root / "capture.json", "unsafe", "../verify.py", ["unit-1"], root, ledger)[0]
        outside = root.parent / "outside-verifier.py"
        outside.write_text("# outside\n", encoding="utf-8")
        (root / "linked-verify.py").symlink_to(outside)
        assert "missing verifier" in register({"schema_version": 1, "entries": []}, capture, capture_path, "linked", "linked-verify.py", ["unit-1"], root, ledger)[0]
        loop_capture = root / "loop-capture.json"
        loop_capture.symlink_to(loop_capture)
        assert "missing capture manifest" in register(
            {"schema_version": 1, "entries": []}, capture, loop_capture,
            "loop", "verify.py", ["unit-1"], root, ledger)[0]
        linked_capture = root / "linked-capture.json"
        linked_capture.symlink_to(capture_path)
        assert "missing capture manifest" in register(
            {"schema_version": 1, "entries": []}, capture, linked_capture,
            "linked", "verify.py", ["unit-1"], root, ledger)[0]
        linked_capture_dir = root / "linked-capture-dir"
        linked_capture_dir.symlink_to(root)
        nested_capture = linked_capture_dir / "capture.json"
        assert "missing capture manifest" in register(
            {"schema_version": 1, "entries": []}, capture, nested_capture,
            "linked directory", "verify.py", ["unit-1"], root, ledger)[0]
    print("PASS: canonical evidence registration validates and deduplicates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
