#!/usr/bin/env python3
"""Regression test for object-state helper PC coverage analysis."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "von/tools/analyze_object_state_coverage.py"


def main() -> int:
    pcs = """# set=vonj seconds=60 frames=3600
00079050
000790a4
00079400
000795a8
000795b8
# visited=5
"""
    with tempfile.TemporaryDirectory(prefix="von-object-state-") as directory:
        pcs_path = Path(directory) / "fixture.pcs"
        report_path = Path(directory) / "report.json"
        pcs_path.write_text(pcs, encoding="utf-8")
        result = subprocess.run(
            ["python3", TOOL, pcs_path, "--json", report_path, "--root", directory],
            check=True,
            capture_output=True,
            text=True,
        )
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if report["visited_states"] != [0, 5, 8, 9]:
            raise SystemExit(f"unexpected visited states: {report}")
        if report["unvisited_states"] != [1, 2, 3, 4, 6, 7]:
            raise SystemExit(f"unexpected unvisited states: {report}")
        if "visited states: 0, 5, 8, 9" not in result.stdout:
            raise SystemExit(f"unexpected CLI output: {result.stdout!r}")
        outside = Path(directory).parent / "outside-object-state.json"
        result = subprocess.run(
            ["python3", TOOL, pcs_path, "--json", outside, "--root", directory],
            capture_output=True, text=True, check=False,
        )
        assert result.returncode == 1
        assert "JSON output path escapes root" in result.stdout
    print("PASS: object-state helper state-entry coverage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
