#!/usr/bin/env python3
"""Run the evidence, ledger, lifecycle, and optional asset-pack gates together."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from evidence_manifest import validate as validate_evidence
from reconstruction_ledger import load, validate as validate_ledger, validate_lifecycle
from validate_asset_pack import validate as validate_pack


def validate_workflow(root: Path, ledger_path: Path, evidence_path: Path,
                      strict_lifecycle: bool = False, asset_pack_path: Path | None = None,
                      run_verifiers: bool = False, rom_manifest_path: Path | None = None,
                      expected_tool_revision: str | None = None,
                      expected_map_revision: str | None = None) -> list[str]:
    ledger = load(ledger_path)
    evidence = load(evidence_path)
    errors = [f"ledger: {error}" for error in validate_ledger(ledger, root)]
    errors.extend(f"evidence: {error}" for error in validate_evidence(evidence, ledger, root))
    if run_verifiers:
        for entry in evidence.get("entries", []):
            if not entry.get("canonical") or not entry.get("verifier"):
                continue
            completed = subprocess.run([sys.executable, entry["verifier"]], cwd=root,
                                       capture_output=True, text=True, check=False)
            if completed.returncode:
                detail = completed.stderr.strip() or completed.stdout.strip()
                errors.append(f"verifier {entry['id']} failed: {detail}")
    if strict_lifecycle:
        errors.extend(f"lifecycle: {error}" for error in validate_lifecycle(ledger, evidence, root))
    if asset_pack_path:
        pack = load(asset_pack_path)
        errors.extend(f"asset-pack: {error}" for error in validate_pack(
            pack, evidence, root, rom_manifest_path, expected_tool_revision,
            expected_map_revision))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--ledger", type=Path, default=Path("von/reconstruction_ledger.json"))
    parser.add_argument("--evidence", type=Path, default=Path("von/evidence/manifest.json"))
    parser.add_argument("--strict-lifecycle", action="store_true")
    parser.add_argument("--asset-pack", type=Path)
    parser.add_argument("--rom-manifest", type=Path,
                        help="optional ROM manifest used to verify asset-pack identity")
    parser.add_argument("--tool-revision",
                        help="optional expected asset-pack tool revision")
    parser.add_argument("--map-revision",
                        help="optional expected asset-pack map revision")
    parser.add_argument("--run-verifiers", action="store_true")
    args = parser.parse_args()
    errors = validate_workflow(args.root, args.ledger, args.evidence, args.strict_lifecycle,
                               args.asset_pack, args.run_verifiers, args.rom_manifest,
                               args.tool_revision, args.map_revision)
    if errors:
        print(f"Evidence workflow validation: {len(errors)} error(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Evidence workflow validation: all selected gates pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
