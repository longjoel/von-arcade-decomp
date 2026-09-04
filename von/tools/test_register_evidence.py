#!/usr/bin/env python3
"""Contract tests for canonical evidence registration."""

from __future__ import annotations

import copy
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
        artifact.write_text('{"capture_id":"capture-v1","tier":"A"}\n', encoding="utf-8")
        capture = {
            "schema_version": 1, "id": "capture-v1", "objective": "pilot",
            "stimulus": {"kind": "input-free-attract", "seconds": 1},
            "configuration": {"set": "vonj", "mame_revision": "abc", "patch_profile": "none", "execution_engine": "interpreter"},
            "command": ["mame", "vonj"],
            "isolation": {"cfg_directory": "cfg", "nvram_directory": "nvram", "state_directory": "state"},
            "coverage_report": "summary.json", "inputs": [], "artifacts": [entry(artifact, root)],
        }
        for field in ("cfg_directory", "nvram_directory", "state_directory"):
            capture["isolation"][f"{field}_sha256"] = directory_sha256(root / capture["isolation"][field])
        verifier = root / "verify.py"
        verifier.write_text("# verifier\n", encoding="utf-8")
        capture_path = root / "capture.json"
        capture_path.write_text("{}\n", encoding="utf-8")
        manifest = {"schema_version": 1, "entries": []}
        ledger = {"images": [{"work_units": [{"id": "unit-1"}]}]}
        assert not register(manifest, capture, capture_path, "pilot capture", "verify.py", ["unit-1"], root, ledger)
        assert manifest["entries"][0]["canonical"] is True
        assert manifest["entries"][0]["capture_manifest"] == "capture.json"
        assert ledger["images"][0]["work_units"][0]["evidence"] == ["capture-v1"]
        broken = copy.deepcopy(manifest)
        assert register(broken, capture, capture_path, "duplicate", "verify.py", ["unit-1"], root)
        assert "unknown ledger consumers" in register({}, capture, root / "capture.json", "unknown", "verify.py", ["missing"], root, ledger)[0]
        assert "missing verifier" in register({}, capture, root / "capture.json", "unsafe", "../verify.py", ["unit-1"], root, ledger)[0]
    print("PASS: canonical evidence registration validates and deduplicates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
