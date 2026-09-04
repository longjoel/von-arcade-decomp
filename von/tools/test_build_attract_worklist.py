#!/usr/bin/env python3
"""Contract tests for Tier A worklist admission and WIP limits."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "von/tools/build_attract_worklist.py"


def run(coverage: dict, ledger: dict, work: Path,
        comparison: dict | None = None) -> subprocess.CompletedProcess[str]:
    coverage_path = work / "coverage.json"
    ledger_path = work / "ledger.json"
    output_path = work / "worklist.json"
    markdown_path = work / "worklist.md"
    coverage_path.write_text(json.dumps(coverage), encoding="utf-8")
    ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
    comparison_path = work / "comparison.json"
    if comparison is not None:
        comparison_path.write_text(json.dumps(comparison), encoding="utf-8")
    command = [sys.executable, str(TOOL), "--coverage", str(coverage_path), "--ledger", str(ledger_path),
               "--json", str(output_path), "--markdown", str(markdown_path)]
    if comparison is not None:
        command.extend(["--comparison", str(comparison_path)])
    return subprocess.run(
        command,
        cwd=ROOT, capture_output=True, text=True, check=False,
    )


def main() -> int:
    coverage = {"schema_version": 1, "tier": "A", "edge_semantics": "possible_static_edges",
                "observed_entry_points": ["0x100"],
                "possible_static_edges": [{"target": "0x100"}]}
    ledger = {"images": [{"name": "maincpu", "work_units": []}]}
    with tempfile.TemporaryDirectory() as directory:
        work = Path(directory)
        result = run(coverage, ledger, work)
        assert result.returncode == 0, result.stderr
        output = json.loads((work / "worklist.json").read_text(encoding="utf-8"))
        assert output["coverage_tier"] == "A"
        assert output["edge_semantics"] == "possible_static_edges"
        assert output["modeled_wip_limit"] == 1
        assert output["active_modeled_units"] == []
        assert output["units"][0]["possible_static_edges"] == 1
        assert "observed_call_edges" not in output["units"][0]
        linked_json = work / "linked-worklist.json"
        linked_json.symlink_to(work / "worklist.json")
        linked_result = subprocess.run(
            [sys.executable, str(TOOL), "--coverage", str(work / "coverage.json"),
             "--ledger", str(work / "ledger.json"), "--json", str(linked_json),
             "--markdown", str(work / "worklist-linked.md")],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert linked_result.returncode == 1
        assert "JSON output path must not be a symlink" in linked_result.stdout
        comparison = {"missing_dynamic_edges": [["0x200", "0x100"], ["0x300", "0x400"]],
                      "missed_checkpoints": ["scheduler"], "first_divergence_index": 12}
        result = run(coverage, ledger, work, comparison)
        assert result.returncode == 0, result.stderr
        causal = json.loads((work / "worklist.json").read_text(encoding="utf-8"))
        assert causal["missing_dynamic_edge_count"] == 2
        assert causal["missed_checkpoints"] == ["scheduler"]
        assert causal["checkpoint_distance"] == 1
        assert causal["first_divergence_index"] == 12
        assert causal["units"][0]["causal_priority"] == 0
        assert causal["units"][0]["dynamic_dependencies"] == [["0x00000200", "0x00000100"]]
        assert causal["dynamic_targets_added"] == 1
        dynamic_target = next(unit for unit in causal["units"] if unit["entry"] == "0x00000400")
        assert dynamic_target["discovery"] == "tier-b-dynamic-target"
        assert dynamic_target["stage"] == "planned"
        invalid_comparison = {"missing_dynamic_edges": ["malformed"]}
        assert run(coverage, ledger, work, invalid_comparison).returncode != 0
        invalid_comparison = {"missing_dynamic_edges": [], "missed_checkpoints": "scheduler"}
        assert run(coverage, ledger, work, invalid_comparison).returncode != 0
        invalid = dict(coverage)
        invalid["edge_semantics"] = "executed_direct_edges"
        assert run(invalid, ledger, work).returncode != 0
        invalid = dict(coverage)
        invalid["possible_static_edges"] = "malformed"
        assert run(invalid, ledger, work).returncode != 0
        invalid = dict(coverage)
        invalid["possible_static_edges"] = [{}]
        assert run(invalid, ledger, work).returncode != 0
        invalid = dict(coverage)
        invalid["observed_entry_points"] = [True]
        assert run(invalid, ledger, work).returncode != 0
        invalid_ledger = {"images": {}}
        assert run(coverage, invalid_ledger, work).returncode != 0
        over_limit = {"images": [{"name": "maincpu", "work_units": [
            {"id": "one", "stage": "modeled", "active": True},
            {"id": "two", "stage": "modeled", "active": True},
        ]}]}
        assert "work-in-progress limit" in run(coverage, over_limit, work).stderr
    print("PASS: worklist admits Tier A and enforces one active modeled unit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
