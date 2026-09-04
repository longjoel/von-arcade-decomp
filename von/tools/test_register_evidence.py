#!/usr/bin/env python3
"""Contract tests for canonical evidence registration."""

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
from pathlib import Path

from capture_manifest import directory_sha256, entry
from register_evidence import register


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for name in ("cfg", "nvram", "state"):
            (root / name).mkdir()
        artifact = root / "summary.json"
        artifact.write_text('{"capture_id":"capture-v1","tier":"A","edge_semantics":"possible_static_edges"}\n', encoding="utf-8")
        capture = {
            "schema_version": 1, "id": "capture-v1", "objective": "pilot",
            "stimulus": {"kind": "input-free-attract", "seconds": 1},
            "configuration": {"set": "vonj", "mame_revision": "abc", "patch_profile": "none", "execution_engine": "interpreter"},
            "command": ["mame", "vonj", "-cfg_directory", str(root / "cfg"),
                         "-nvram_directory", str(root / "nvram"),
                         "-state_directory", str(root / "state")],
            "isolation": {"cfg_directory": "cfg", "nvram_directory": "nvram", "state_directory": "state"},
            "coverage_report": "summary.json", "inputs": [], "artifacts": [entry(artifact, root)],
        }
        for field in ("cfg_directory", "nvram_directory", "state_directory"):
            capture["isolation"][f"{field}_sha256"] = directory_sha256(root / capture["isolation"][field])
        verifier = root / "verify.py"
        verifier.write_text("# verifier\n", encoding="utf-8")
        capture_path = root / "capture.json"
        capture_path.write_text(json.dumps(capture) + "\n", encoding="utf-8")
        manifest = {"schema_version": 1, "entries": []}
        ledger = {"images": [{"work_units": [{"id": "unit-1"}]}]}
        assert not register(manifest, capture, capture_path, "pilot capture", "verify.py", ["unit-1"], root, ledger)
        assert manifest["entries"][0]["canonical"] is True
        assert manifest["entries"][0]["capture_manifest"] == "capture.json"
        assert manifest["entries"][0]["capture_manifest_sha256"] == hashlib.sha256(
            capture_path.read_bytes()).hexdigest()
        assert ledger["images"][0]["work_units"][0]["evidence"] == ["capture-v1"]
        mismatched_capture = copy.deepcopy(capture)
        mismatched_capture["objective"] = "different"
        assert any("differs from on-disk" in error for error in register(
            {}, mismatched_capture, capture_path, "mismatch", "verify.py", ["unit-1"], root))
        partially_invalid = {"images": [{"work_units": [
            {"id": "unit-1"}, {"id": "unit-2", "evidence": "invalid"}
        ]}]}
        before = copy.deepcopy(partially_invalid)
        assert any("invalid evidence list" in error for error in register(
            {}, capture, capture_path, "partial", "verify.py", ["unit-1", "unit-2"],
            root, partially_invalid))
        assert partially_invalid == before
        assert any("consumers must be unique" in error for error in register(
            {}, capture, capture_path, "duplicate consumers", "verify.py",
            ["unit-1", "unit-1"], root, ledger))
        broken = copy.deepcopy(manifest)
        assert register(broken, capture, capture_path, "duplicate", "verify.py", ["unit-1"], root)
        assert "unknown ledger consumers" in register({}, capture, root / "capture.json", "unknown", "verify.py", ["missing"], root, ledger)[0]
        assert "missing verifier" in register({}, capture, root / "capture.json", "unsafe", "../verify.py", ["unit-1"], root, ledger)[0]
    print("PASS: canonical evidence registration validates and deduplicates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
