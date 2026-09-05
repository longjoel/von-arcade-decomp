#!/usr/bin/env python3
"""Validate the reconstruction ledger and report union-based code coverage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from evidence_manifest import validate as validate_evidence
from reconstruction_ledger import code_coverage, load, validate, validate_lifecycle


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", nargs="?", type=Path, default=Path("von/reconstruction_ledger.json"))
    parser.add_argument("--strict-lifecycle", action="store_true",
                        help="enforce stage-specific promotion evidence")
    parser.add_argument("--evidence-manifest", type=Path,
                        default=Path("von/evidence/manifest.json"))
    args = parser.parse_args()
    root = Path.cwd().resolve()
    paths = [("ledger", args.ledger)]
    if args.strict_lifecycle:
        paths.append(("evidence manifest", args.evidence_manifest))
    for label, path in paths:
        if path.is_symlink():
            print(f"Ledger validation: {label} path must not be a symlink")
            return 1
        try:
            path.resolve().relative_to(root)
        except (OSError, RuntimeError, ValueError):
            print(f"Ledger validation: {label} path escapes root: {path}")
            return 1
        if not path.is_file():
            print(f"Ledger validation: missing {label}: {path}")
            return 1
    try:
        ledger = load(args.ledger)
        evidence = load(args.evidence_manifest) if args.strict_lifecycle else None
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
        print(f"Ledger validation: unable to read validation document: {error}")
        return 1
    errors = validate(ledger, root)
    if args.strict_lifecycle:
        errors.extend(
            f"evidence manifest: {error}"
            for error in validate_evidence(evidence, ledger, root)
        )
        errors.extend(validate_lifecycle(ledger, evidence, root))
    if errors:
        print(f"Ledger validation: {len(errors)} error(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    coverage = code_coverage(ledger)
    print(f"Ledger validation: 0 errors; physical code union: {coverage['total']:,} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
