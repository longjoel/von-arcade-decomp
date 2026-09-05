#!/usr/bin/env python3
"""Check that the SHARC evidence inventory consumes ledger schema v2."""

from pathlib import Path
import subprocess
import tempfile
import sys

from inventory_sharc_evidence import build_report


def main() -> int:
    report = build_report(Path.cwd())
    assert report["schema_version"] == 2
    assert report["ledger"]["entries"] > 0
    assert "modeled" in report["ledger"]["stages"]
    assert not report["ledger"]["whole_ledger_validation_errors"]
    with tempfile.TemporaryDirectory() as directory:
        outside = Path(directory) / "inventory.json"
        result = subprocess.run(
            [sys.executable, "von/tools/inventory_sharc_evidence.py", "--root", str(Path.cwd()),
             "--json", str(outside)], capture_output=True, text=True, check=False)
        assert result.returncode == 1
        assert "JSON output path escapes root" in result.stdout
    print("PASS: SHARC evidence inventory uses valid schema-v2 work units")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
