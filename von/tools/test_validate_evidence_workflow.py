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
    with tempfile.TemporaryDirectory(dir=root) as directory:
        malformed_ledger = Path(directory) / "ledger.json"
        malformed_ledger.write_text("[]\n", encoding="utf-8")
        errors = validate_workflow(
            root, malformed_ledger, root / "von/evidence/manifest.json", strict_lifecycle=True)
        assert any("ledger: ledger must be an object" in error for error in errors)
        assert any("evidence: ledger must be an object" in error for error in errors)
    errors = validate_workflow(
        root, root / "von/reconstruction_ledger.json", root / "von/evidence/manifest.json",
        check_generated=True, generated_coverage_path=root / "von/build/attract-coverage/vonj-attract-60s.json",
        generated_worklist_path=root / "von/attract_worklist.json",
        generated_status_path=root / "von/generated-status.md",
    )
    assert any("generated:" in error for error in errors)
    with tempfile.TemporaryDirectory(dir=root) as directory:
        comparison = Path(directory) / "comparison.json"
        comparison.write_text(json.dumps({"missing_dynamic_edges": [],
                                          "missed_checkpoints": []}), encoding="utf-8")
        # The tracked worklist is Tier A-only; supplying a causal source must
        # therefore make freshness validation reject it rather than ignore it.
        errors = validate_workflow(
            root, root / "von/reconstruction_ledger.json", root / "von/evidence/manifest.json",
            check_generated=True,
            generated_coverage_path=root / "von/build/attract-coverage/vonj-attract-60s.json",
            generated_worklist_path=root / "von/attract_worklist.json",
            generated_status_path=root / "von/generated-status.md",
            generated_comparison_path=comparison,
        )
        assert any("stale worklist JSON" in error for error in errors)
    outside = Path(tempfile.gettempdir()) / "von-generated-status-outside.md"
    errors = validate_workflow(
        root, root / "von/reconstruction_ledger.json", root / "von/evidence/manifest.json",
        check_generated=True,
        generated_coverage_path=outside,
        generated_worklist_path=root / "von/attract_worklist.json",
        generated_status_path=root / "von/generated-status.md",
    )
    assert any("coverage path escapes root" in error for error in errors)
    with tempfile.TemporaryDirectory(dir=root) as directory:
        loop = Path(directory) / "loop.json"
        loop.symlink_to(loop)
        errors = validate_workflow(
            root, root / "von/reconstruction_ledger.json", root / "von/evidence/manifest.json",
            check_generated=True, generated_coverage_path=loop,
            generated_worklist_path=root / "von/attract_worklist.json",
            generated_status_path=root / "von/generated-status.md",
        )
        assert any("unable to read coverage JSON" in error for error in errors)
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
    missing_pack = root / "von/build/missing-pack.json"
    errors = validate_workflow(
        root, root / "von/reconstruction_ledger.json", root / "von/evidence/manifest.json",
        asset_pack_path=missing_pack)
    assert any("missing pack manifest" in error for error in errors)
    with tempfile.TemporaryDirectory(dir=root) as directory:
        linked_pack = Path(directory) / "linked-pack.json"
        linked_pack.symlink_to(root / "von/evidence/manifest.json")
        errors = validate_workflow(
            root, root / "von/reconstruction_ledger.json", root / "von/evidence/manifest.json",
            asset_pack_path=linked_pack)
        assert any("must not be a symlink" in error for error in errors)
    print("PASS: combined evidence workflow gates ledger and lifecycle validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
