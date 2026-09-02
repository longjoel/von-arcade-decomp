#!/usr/bin/env python3
"""Tests for schema-v2 migration, validation, and non-duplicated coverage."""

from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path

from migrate_reconstruction_ledger import migrate
from reconstruction_ledger import code_coverage, validate


def main() -> int:
    old = {"schema_version": 1, "images": [{"name": "maincpu", "size": 256, "slices": [
        {"name": "outer", "start": "0x10", "end": "0x30", "classification": "code", "status": "provisional", "source": "notes.md", "evidence": []},
        {"name": "inner", "start": "0x18", "end": "0x20", "classification": "code", "status": "provisional", "source": "model.c", "evidence": ["von/i960/recovered_example.c"]},
        {"name": "contract", "classification": "behavior", "status": "provisional", "source": "contract.md", "evidence": []},
    ]}]}
    ledger = migrate(old)
    assert not validate(ledger)
    assert code_coverage(ledger)["total"] == 0x20
    assert ledger["images"][0]["work_units"][1]["stage"] == "modeled"
    assert ledger["images"][0]["work_units"][2]["stage"] == "planned"
    assert "sources" in ledger["images"][0]["work_units"][0]
    broken = copy.deepcopy(ledger)
    broken["images"][0]["physical_ranges"].append({"id": "overlap", "start": "0x20", "end": "0x40", "classification": "code"})
    assert any("overlaps" in error for error in validate(broken))
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "roundtrip.json"
        path.write_text(json.dumps(ledger), encoding="utf-8")
        assert json.loads(path.read_text(encoding="utf-8"))["schema_version"] == 2
    print("PASS: ledger v1 migration, schema-v2 validation, and union coverage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
