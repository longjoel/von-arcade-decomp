#!/usr/bin/env python3
"""Contract tests for zero-trust evidence inventory records."""

from __future__ import annotations

import tempfile
from pathlib import Path

from inventory_evidence import apply_relations, duplicate_groups, inventory_path, relation_errors


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
            assert "escapes root" in str(error)
        else:
            raise AssertionError("external inventory symlink was accepted")
    print("PASS: evidence inventory records hashes and cleanup decisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
