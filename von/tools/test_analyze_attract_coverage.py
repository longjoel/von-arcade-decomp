#!/usr/bin/env python3
"""Regression tests for the Tier A attract coverage terminology."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "von/tools/analyze_attract_coverage.py"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        work = Path(directory)
        (work / "pcs").write_text("100\n104\n108\n200\n", encoding="ascii")
        (work / "listing").write_text(
            "100: call 0x00000200\n"
            "104: call 0x00000300\n"
            "108: nop\n"
            "200: ret\n",
            encoding="ascii",
        )
        report_path = work / "report.json"
        subprocess.run(
            [
                sys.executable,
                str(TOOL),
                "--pcs",
                str(work / "pcs"),
                "--listing",
                str(work / "listing"),
                "--json",
                str(report_path),
                "--markdown",
                str(work / "report.md"),
                "--root",
                str(work),
                "--capture-id",
                "fixture-attract-1",
                "--phase",
                "startup",
            ],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        report = json.loads(report_path.read_text(encoding="utf-8"))
        assert report["tier"] == "A"
        assert report["canonical"] is False
        assert report["registration"] == "discovery-only"
        assert report["capture_id"] == "fixture-attract-1"
        assert report["phase"] == "startup"
        assert report["edge_semantics"] == "possible_static_edges"
        assert report["observed_entry_points"] == ["0x00000200"]
        assert len(report["possible_static_edges"]) == 1
        assert "executed_direct_edges" not in report
        assert "executed_direct_targets" not in report
        outside_output = work.parent / "outside-attract-coverage.json"
        result = subprocess.run(
            [sys.executable, str(TOOL), "--root", str(work), "--pcs", str(work / "pcs"),
             "--listing", str(work / "listing"), "--json", str(outside_output),
             "--markdown", str(work / "report-2.md"), "--capture-id", "fixture-attract-2"],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert result.returncode == 1
        assert "JSON output path escapes root" in result.stdout
    print("PASS: Tier A coverage reports possible static edges")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
