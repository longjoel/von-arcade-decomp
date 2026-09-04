#!/usr/bin/env python3
"""Run the evidence, ledger, lifecycle, and optional asset-pack gates together."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from evidence_manifest import rooted, validate as validate_evidence
from reconstruction_ledger import load, validate as validate_ledger, validate_lifecycle
from validate_asset_pack import validate as validate_pack


def validate_workflow(root: Path, ledger_path: Path, evidence_path: Path,
                      strict_lifecycle: bool = False, asset_pack_path: Path | None = None,
                      run_verifiers: bool = False, rom_manifest_path: Path | None = None,
                      expected_tool_revision: str | None = None,
                      expected_map_revision: str | None = None,
                      check_generated: bool = False,
                      generated_coverage_path: Path | None = None,
                      generated_worklist_path: Path | None = None,
                      generated_status_path: Path | None = None,
                      generated_comparison_path: Path | None = None) -> list[str]:
    ledger = load(ledger_path)
    evidence = load(evidence_path)
    errors = [f"ledger: {error}" for error in validate_ledger(ledger, root)]
    errors.extend(f"evidence: {error}" for error in validate_evidence(evidence, ledger, root))
    if run_verifiers:
        for entry in evidence.get("entries", []):
            if not entry.get("canonical") or not entry.get("verifier"):
                continue
            verifier = rooted(root, entry["verifier"])
            if verifier is None or not verifier.is_file():
                errors.append(f"verifier {entry.get('id', '?')} skipped: unsafe or missing path")
                continue
            completed = subprocess.run([sys.executable, str(verifier)], cwd=root,
                                       capture_output=True, text=True, check=False)
            if completed.returncode:
                detail = completed.stderr.strip() or completed.stdout.strip()
                errors.append(f"verifier {entry['id']} failed: {detail}")
    if strict_lifecycle:
        errors.extend(f"lifecycle: {error}" for error in validate_lifecycle(ledger, evidence, root))
    if asset_pack_path:
        if asset_pack_path.is_symlink():
            errors.append(f"asset-pack: pack path must not be a symlink: {asset_pack_path}")
        else:
            try:
                asset_pack_path.resolve().relative_to(root.resolve())
            except (OSError, RuntimeError, ValueError):
                errors.append(f"asset-pack: pack path escapes root: {asset_pack_path}")
            else:
                if not asset_pack_path.is_file():
                    errors.append(f"asset-pack: missing pack manifest: {asset_pack_path}")
                else:
                    try:
                        pack = load(asset_pack_path)
                    except (OSError, ValueError) as error:
                        errors.append(f"asset-pack: unable to read pack manifest: {error}")
                    else:
                        errors.extend(f"asset-pack: {error}" for error in validate_pack(
                            pack, evidence, root, rom_manifest_path, expected_tool_revision,
                            expected_map_revision))
    if check_generated:
        if not all((generated_coverage_path, generated_worklist_path, generated_status_path)):
            errors.append("generated checks require coverage, worklist, and status paths")
        else:
            generated_paths = [
                ("coverage", generated_coverage_path),
                ("worklist", generated_worklist_path),
                ("status", generated_status_path),
            ]
            if generated_comparison_path:
                generated_paths.append(("comparison", generated_comparison_path))
            unsafe_paths = []
            for label, path in generated_paths:
                try:
                    path.resolve().relative_to(root.resolve())
                except (OSError, RuntimeError, ValueError):
                    unsafe_paths.append(f"generated {label} path escapes root: {path}")
            if unsafe_paths:
                errors.extend(unsafe_paths)
                return errors
            from check_generated_status import check as check_status
            from check_generated_worklist import check as check_worklist

            errors.extend(f"generated: {error}" for error in check_status(root, generated_status_path))
            errors.extend(f"generated: {error}" for error in check_worklist(
                generated_coverage_path, ledger_path, generated_worklist_path, root,
                comparison=generated_comparison_path))
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
    parser.add_argument("--check-generated", action="store_true",
                        help="require generated status and worklist files to be current")
    parser.add_argument("--coverage", type=Path,
                        help="Tier A coverage input for --check-generated")
    parser.add_argument("--worklist", type=Path,
                        help="generated worklist for --check-generated")
    parser.add_argument("--status", type=Path,
                        help="generated status Markdown for --check-generated")
    parser.add_argument("--comparison", type=Path,
                        help="optional comparison input used by the generated worklist")
    parser.add_argument("--run-verifiers", action="store_true")
    args = parser.parse_args()
    errors = validate_workflow(args.root, args.ledger, args.evidence, args.strict_lifecycle,
                               args.asset_pack, args.run_verifiers, args.rom_manifest,
                               args.tool_revision, args.map_revision, args.check_generated,
                               args.coverage, args.worklist, args.status, args.comparison)
    if errors:
        print(f"Evidence workflow validation: {len(errors)} error(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Evidence workflow validation: all selected gates pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
