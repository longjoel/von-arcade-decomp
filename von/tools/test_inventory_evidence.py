#!/usr/bin/env python3
"""Contract tests for zero-trust evidence inventory records."""

from __future__ import annotations

import tempfile
import subprocess
import sys
from pathlib import Path

from inventory_evidence import apply_relations, duplicate_groups, inventory_path, relation_errors


ROOT = Path(__file__).resolve().parents[2]
TOOL = Path(__file__).resolve().parent / "inventory_evidence.py"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        generated = root / "von/build/capture.log"
        generated_copy = root / "von/build/capture-copy.log"
        source = root / "von/tools/producer.py"
        ambiguous = root / "old-output.log"
        for path in (generated, source, ambiguous):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(path.name, encoding="utf-8")
        generated_copy.write_text(generated.read_text(encoding="utf-8"), encoding="utf-8")
        tracked = {"von/tools/producer.py"}
        assert inventory_path(generated, root, tracked)["classification"] == "reproducible-generated"
        source_record = inventory_path(source, root, tracked)
        assert source_record["tracked"] is True
        assert source_record["decision"] == "keep"
        assert inventory_path(ambiguous, root, tracked)["decision"] == "quarantine-after-review"
        records = [inventory_path(path, root, tracked) for path in (generated, generated_copy, source, ambiguous)]
        apply_relations(records, {"old-output.log": {"producer": "capture.sh", "consumers": ["review.md"]}})
        assert records[-1]["producer"] == "capture.sh"
        assert records[-1]["consumers"] == ["review.md"]
        groups = duplicate_groups(records)
        assert len(groups) == 1
        assert groups[0]["paths"] == ["von/build/capture-copy.log", "von/build/capture.log"]
        assert groups[0]["aliases"] == ["von/build/capture.log"]
        assert duplicate_groups(list(reversed(records))) == groups
        assert all("sha256" in record for record in records)
        complete = {record["path"]: {"producer": "producer.sh", "consumers": ["review.md"]}
                    for record in records}
        assert relation_errors(records, complete, require_complete=True) == []
        assert any("unknown inventory path" in error for error in relation_errors(
            records, {"missing.log": {}}, require_complete=True))
        incomplete = dict(complete)
        incomplete["old-output.log"] = {"producer": "capture.sh", "consumers": []}
        assert any("non-empty consumers" in error for error in relation_errors(
            records, incomplete, require_complete=True))
        duplicate_consumers = dict(complete)
        duplicate_consumers["old-output.log"] = {
            "producer": "capture.sh", "consumers": ["review.md", "review.md"]}
        assert any("consumers must be unique" in error for error in relation_errors(
            records, duplicate_consumers, require_complete=True))
        outside = root.parent / "outside-inventory-fixture.log"
        outside.write_text("outside", encoding="utf-8")
        escaped = root / "linked.log"
        escaped.symlink_to(outside)
        try:
            inventory_path(escaped, root, set())
        except ValueError as error:
            assert "must not contain symlink components" in str(error)
        else:
            raise AssertionError("external inventory symlink was accepted")
        local_link = root / "local-link.log"
        local_link.symlink_to(generated)
        try:
            inventory_path(local_link, root, set())
        except ValueError as error:
            assert "must not contain symlink components" in str(error)
        else:
            raise AssertionError("internal inventory symlink was accepted")
    with tempfile.TemporaryDirectory(dir=ROOT) as directory:
        temp_root = Path(directory)
        target = temp_root / "output.json"
        target.write_text("existing\n", encoding="utf-8")
        linked_output = temp_root / "linked-output.json"
        linked_output.symlink_to(target)
        cli_result = subprocess.run(
            [sys.executable, str(TOOL), "--root", str(ROOT), "--path",
             "von/tools/test_inventory_evidence.py", "--output", str(linked_output)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert cli_result.returncode == 1
        assert "output path must not contain symlink components" in cli_result.stdout
        linked_output_parent = temp_root / "linked-output-parent"
        linked_output_parent.symlink_to(temp_root, target_is_directory=True)
        cli_result = subprocess.run(
            [sys.executable, str(TOOL), "--root", str(ROOT), "--path",
             "von/tools/test_inventory_evidence.py", "--output",
             str(linked_output_parent / "nested-output.json")],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert cli_result.returncode == 1
        assert "output path must not contain symlink components" in cli_result.stdout
        malformed_relations = temp_root / "malformed-relations.json"
        malformed_relations.write_text("{invalid\n", encoding="utf-8")
        cli_result = subprocess.run(
            [sys.executable, str(TOOL), "--root", str(ROOT), "--path",
             "von/tools/test_inventory_evidence.py", "--output", str(target),
             "--relations", str(malformed_relations)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert cli_result.returncode == 1
        assert "unable to read relations" in cli_result.stdout
        outside_output = ROOT.parent / "outside-inventory.json"
        cli_result = subprocess.run(
            [sys.executable, str(TOOL), "--root", str(ROOT), "--path",
             "von/tools/test_inventory_evidence.py", "--output", str(outside_output)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert cli_result.returncode == 1
        assert "output path escapes root" in cli_result.stdout
    print("PASS: evidence inventory records hashes and cleanup decisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
