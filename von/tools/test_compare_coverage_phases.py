#!/usr/bin/env python3
"""Contract tests for Tier A coverage phase comparison."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from compare_coverage_phases import compare, load_report


ROOT = Path(__file__).resolve().parents[2]
TOOL = Path(__file__).resolve().parent / "compare_coverage_phases.py"


def main() -> int:
    before = {
        "tier": "A", "edge_semantics": "possible_static_edges", "capture_id": "short",
        "phase": "startup", "visited_instruction_count": 4,
        "observed_entry_points": ["0x10"], "possible_static_edges": [{"caller": "0x1", "target": "0x10"}],
        "ranges": [{"start": "0x1", "end": "0x11"}],
    }
    after = {
        "tier": "A", "edge_semantics": "possible_static_edges", "capture_id": "long",
        "phase": "attract", "visited_instruction_count": 9,
        "observed_entry_points": ["0x10", "0x20"],
        "possible_static_edges": [{"caller": "0x1", "target": "0x10"}, {"caller": "0x2", "target": "0x20"}],
        "ranges": [{"start": "0x1", "end": "0x11"}, {"start": "0x20", "end": "0x24"}],
    }
    result = compare(before, after)
    assert result["visited_instruction_delta"] == 5
    assert result["visited_range_delta"] == 1
    assert result["new_observed_entry_points"] == ["0x20"]
    assert result["new_possible_static_edges"] == [{"caller": "0x2", "target": "0x20"}]
    try:
        compare(before, {"tier": "B", "edge_semantics": "executed_edges"})
    except ValueError as error:
        assert "Tier A possible_static_edges" in str(error)
    else:
        raise AssertionError("invalid coverage semantics were accepted")
    invalid_count = dict(before, visited_instruction_count=True)
    try:
        compare(before, invalid_count)
    except ValueError as error:
        assert "nonnegative integer" in str(error)
    else:
        raise AssertionError("invalid instruction count was accepted")
    with tempfile.TemporaryDirectory(dir=ROOT) as directory:
        temp = Path(directory)
        before_path, after_path = temp / "before.json", temp / "after.json"
        before_path.write_text(json.dumps(before), encoding="utf-8")
        after_path.write_text(json.dumps(after), encoding="utf-8")
        output_path = temp / "comparison.json"
        cli_result = subprocess.run(
            [sys.executable, str(TOOL), "--root", str(ROOT), "--before", str(before_path),
             "--after", str(after_path), "--output", str(output_path)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert cli_result.returncode == 0
        outside_output = ROOT.parent / "outside-phase-comparison.json"
        cli_result = subprocess.run(
            [sys.executable, str(TOOL), "--root", str(ROOT), "--before", str(before_path),
             "--after", str(after_path), "--output", str(outside_output)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert cli_result.returncode == 1
        assert "output path escapes root" in cli_result.stdout
    print("PASS: Tier A coverage phase comparison reports discovery deltas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
