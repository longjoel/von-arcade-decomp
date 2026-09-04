#!/usr/bin/env python3
"""Integration test for the combined evidence workflow validator."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from validate_evidence_workflow import validate_workflow


def main() -> int:
    root = Path.cwd()
    assert not validate_workflow(
        root, root / "von/reconstruction_ledger.json", root / "von/evidence/manifest.json"
    )
    assert not validate_workflow(
        root, root / "von/reconstruction_ledger.json", root / "von/evidence/manifest.json",
        run_verifiers=True,
    )
    errors = validate_workflow(
        root, root / "von/reconstruction_ledger.json", root / "von/evidence/manifest.json",
        strict_lifecycle=True,
    )
    assert any("lifecycle:" in error for error in errors)
    unsafe = {
        "schema_version": 1,
        "entries": [{"id": "unsafe", "canonical": True, "verifier": "/tmp/not-a-verifier.py"}],
    }
    with tempfile.TemporaryDirectory() as directory:
        unsafe_path = Path(directory) / "unsafe-evidence.json"
        unsafe_path.write_text(json.dumps(unsafe), encoding="utf-8")
        errors = validate_workflow(root, root / "von/reconstruction_ledger.json", unsafe_path,
                                   run_verifiers=True)
        assert any("skipped: unsafe" in error for error in errors)
    print("PASS: combined evidence workflow gates ledger and lifecycle validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
