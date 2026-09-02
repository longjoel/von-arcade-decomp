#!/usr/bin/env python3
"""Check that the SHARC evidence inventory consumes ledger schema v2."""

from pathlib import Path

from inventory_sharc_evidence import build_report


def main() -> int:
    report = build_report(Path.cwd())
    assert report["schema_version"] == 2
    assert report["ledger"]["entries"] > 0
    assert "modeled" in report["ledger"]["stages"]
    assert not report["ledger"]["whole_ledger_validation_errors"]
    print("PASS: SHARC evidence inventory uses valid schema-v2 work units")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
