#!/usr/bin/env python3
"""Contract tests for the non-destructive evidence cleanup planner."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from plan_evidence_cleanup import plan, validate_inventory


ROOT = Path(__file__).resolve().parents[2]
TOOL = Path(__file__).resolve().parent / "plan_evidence_cleanup.py"


def record(path: str, classification: str, size: int, producer: str | None = "capture.sh",
           consumers: list[str] | None = None) -> dict:
    return {
        "path": path, "bytes": size, "sha256": "a" * 64, "tracked": False,
        "producer": producer, "consumers": consumers if consumers is not None else ["review.md"],
        "classification": classification,
        "decision": {
            "canonical-evidence": "keep-with-manifest",
            "reproducible-generated": "delete-after-recipe-review",
            "legacy-or-ambiguous": "quarantine-after-review",
        }.get(classification, "keep"),
    }


def main() -> int:
    inventory = {
        "schema_version": 1,
        "files": [
            record("von/evidence/manifest.json", "canonical-evidence", 10),
            record("von/build/output.bin", "reproducible-generated", 20),
            record("old/capture.log", "legacy-or-ambiguous", 30, None, []),
        ],
        "duplicate_groups": [],
    }
    result = plan(inventory, "b" * 64)
    assert result["kind"] == "von-evidence-cleanup-plan"
    assert result["mutation"] == "none"
    assert result["review_required"] is True
    assert result["incomplete_provenance_paths"] == ["old/capture.log"]
    assert result["summary"]["remove-after-review"] == {"files": 1, "bytes": 20}
    assert result["disposition_summary"] == {
        "retained": {"files": 1, "bytes": 10},
        "compressed": {"files": 0, "bytes": 0},
        "quarantined": {"files": 1, "bytes": 30},
        "eligible_for_deletion": {"files": 1, "bytes": 20},
    }
    broken = dict(inventory, duplicate_groups=[{"sha256": "b" * 64,
                                                "paths": ["missing", "old/capture.log"],
                                                "aliases": ["old/capture.log"]}])
    assert any("unknown inventory path" in error for error in validate_inventory(broken))
    broken = dict(inventory, duplicate_groups=[{"sha256": "b" * 64,
                                                "paths": ["old/capture.log", "von/build/output.bin"],
                                                "aliases": ["von/build/output.bin"]}])
    assert any("path hash differs" in error for error in validate_inventory(broken))
    broken = dict(inventory, duplicate_groups=[{"sha256": "a" * 64,
                                                "paths": ["von/build/output.bin", "old/capture.log"],
                                                "aliases": []}])
    assert any("aliases must equal" in error for error in validate_inventory(broken))
    assert [item["action"] for item in result["actions"]] == [
        "quarantine-after-review", "remove-after-review", "retain"
    ]
    broken = dict(inventory, files=[record("../escape", "legacy-or-ambiguous", 1)])
    assert any("safe relative path" in error for error in validate_inventory(broken))
    broken = dict(inventory, files=[record("bad", "legacy-or-ambiguous", 1)])
    broken["files"][0]["sha256"] = "A" * 64
    assert any("lowercase" in error for error in validate_inventory(broken))
    with tempfile.TemporaryDirectory(dir=ROOT) as directory:
        temp = Path(directory)
        inventory_path = temp / "inventory.json"
        inventory_path.write_text(json.dumps(inventory), encoding="utf-8")
        output_path = temp / "plan.json"
        cli_result = subprocess.run(
            [sys.executable, str(TOOL), "--inventory", str(inventory_path),
             "--output", str(output_path)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert cli_result.returncode == 0
        linked_output = temp / "linked-plan.json"
        linked_output.symlink_to(output_path)
        cli_result = subprocess.run(
            [sys.executable, str(TOOL), "--inventory", str(inventory_path),
             "--output", str(linked_output)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert cli_result.returncode == 1
        assert "output path must not be a symlink" in cli_result.stdout
        malformed_inventory = temp / "malformed.json"
        malformed_inventory.write_text("{invalid\n", encoding="utf-8")
        cli_result = subprocess.run(
            [sys.executable, str(TOOL), "--inventory", str(malformed_inventory),
             "--output", str(temp / "malformed-plan.json")],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert cli_result.returncode == 1
        assert "Expecting property name" in cli_result.stdout
    print("PASS: evidence cleanup planner emits reviewed non-destructive actions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
