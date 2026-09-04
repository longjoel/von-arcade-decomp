#!/usr/bin/env python3
"""Contract tests for non-destructive worklist freshness checking."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from check_generated_worklist import GENERATOR, check


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    coverage = {"schema_version": 1, "tier": "A", "edge_semantics": "possible_static_edges",
                "observed_entry_points": ["0x100"], "possible_static_edges": []}
    ledger = {"images": [{"name": "maincpu", "work_units": []}]}
    with tempfile.TemporaryDirectory() as directory:
        work = Path(directory)
        coverage_path, ledger_path = work / "coverage.json", work / "ledger.json"
        coverage_path.write_text(json.dumps(coverage), encoding="utf-8")
        ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
        expected = work / "worklist.json"
        subprocess.run([sys.executable, str(GENERATOR), "--coverage", str(coverage_path), "--ledger", str(ledger_path),
                        "--json", str(expected), "--markdown", str(work / "worklist.md")],
                       cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
        markdown = work / "worklist.md"
        assert not check(coverage_path, ledger_path, expected, ROOT, markdown)
        markdown.write_text(markdown.read_text(encoding="utf-8") + "stale\n", encoding="utf-8")
        assert any("Markdown" in error for error in check(coverage_path, ledger_path, expected, ROOT, markdown))
        subprocess.run([sys.executable, str(GENERATOR), "--coverage", str(coverage_path), "--ledger", str(ledger_path),
                        "--json", str(expected), "--markdown", str(markdown)],
                       cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
        expected.write_text(expected.read_text(encoding="utf-8").replace('"schema_version": 1', '"schema_version": 9', 1), encoding="utf-8")
        assert check(coverage_path, ledger_path, expected, ROOT)
        coverage_path.write_text("[]", encoding="utf-8")
        assert any("coverage JSON object" in error for error in
                   check(coverage_path, ledger_path, expected, ROOT))
        coverage_path.write_text("{invalid", encoding="utf-8")
        assert any("unable to read coverage JSON" in error for error in
                   check(coverage_path, ledger_path, expected, ROOT))
    print("PASS: worklist freshness checker detects stale generated output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
