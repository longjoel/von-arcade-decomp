#!/usr/bin/env python3
"""Validate the reconstruction ledger and report union-based code coverage."""

from __future__ import annotations

import argparse
from pathlib import Path

from reconstruction_ledger import code_coverage, load, validate, validate_lifecycle


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", nargs="?", type=Path, default=Path("von/reconstruction_ledger.json"))
    parser.add_argument("--strict-lifecycle", action="store_true",
                        help="enforce stage-specific promotion evidence")
    parser.add_argument("--evidence-manifest", type=Path,
                        default=Path("von/evidence/manifest.json"))
    args = parser.parse_args()
    ledger = load(args.ledger)
    errors = validate(ledger, Path.cwd())
    if args.strict_lifecycle:
        errors.extend(validate_lifecycle(
            ledger, load(args.evidence_manifest), Path.cwd()
        ))
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
