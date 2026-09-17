#!/usr/bin/env python3
"""Synthetic exact-stack tests for analyze_transform_lineage.py."""

import json
from pathlib import Path

from analyze_transform_lineage import LineageError, analyze


I = [0x3F800000, 0, 0, 0, 0x3F800000, 0, 0, 0, 0x3F800000, 0, 0, 0]
A = I[:9] + [0x3F800000, 0, 0]
B = I[:9] + [0, 0x40000000, 0]
C = I[:9] + [0, 0, 0x40400000]


def event(event_id, kind, **fields):
    return {"event_id": event_id, "kind": kind, **fields}


def valid_fixture():
    # Object-root siblings, a deep child, and a marker-rooted optional branch.
    return {"events": [
        event(1, "root", name="object", root_kind="object_root", matrix_words=I),
        event(2, "root", name="marker:2", root_kind="marker", matrix_words=I,
              select=False),
        event(3, "push", depth=1, base_words=I),
        event(4, "commit", depth=1, destination="d0", oba="0x009e0001",
              source_stream="body", record_slot=0, matrix_words=A),
        event(5, "push", depth=2, base_words=A),
        event(6, "commit", depth=2, destination="d1", oba="0x009e0002",
              source_stream="body", record_slot=1, matrix_words=B),
        event(7, "pop", depth=2, restored_words=A),
        event(8, "pop", depth=1, restored_words=I),
        event(9, "push", depth=1, base_words=I),
        event(10, "commit", depth=1, destination="d2", oba="0x009e0003",
              source_stream="skeleton", record_slot=0, matrix_words=C),
        event(11, "pop", depth=1, restored_words=I),
        event(12, "load", source="marker:2", matrix_words=I),
        event(13, "push", depth=1, base_words=I),
        event(14, "commit", depth=1, destination="d3", oba="0x009e0004",
              source_stream="option", record_slot=0, matrix_words=C),
        event(15, "pop", depth=1, restored_words=I),
        event(16, "submit", destination="d0", oba="0x009e0001"),
        event(17, "submit", destination="d1", oba="0x009e0002"),
        event(18, "submit", destination="d2", oba="0x009e0003"),
        event(19, "submit", destination="d3", oba="0x009e0004", active=False),
    ]}


def expect_error(document, fragment):
    try:
        analyze(document)
    except LineageError as error:
        assert fragment in str(error), (fragment, str(error))
    else:
        raise AssertionError(f"expected LineageError containing {fragment!r}")


def main():
    schema = json.loads((Path(__file__).resolve().parents[1] /
                         "render-contract.schema.json").read_text())
    assert schema["properties"]["schema_version"]["const"] == 1
    assert schema["$defs"]["part"]["additionalProperties"] is False
    assert schema["$defs"]["parent"]["oneOf"][2]["properties"]["slot"]["maximum"] == 5

    result = analyze(valid_fixture())
    assert [part["parent"]["source"] for part in result["parts"]] == [
        "object", "part:4:0x009e0001", "object", "marker:2"]
    assert [submission["active"] for submission in result["submissions"]] == [
        True, True, True, False]

    ambiguous = {"events": [
        event(1, "root", name="object", root_kind="object_root", matrix_words=I),
        event(2, "root", name="marker:0", root_kind="marker", matrix_words=I,
              select=False),
        # Select a different current matrix, leaving two exact candidates for I.
        event(3, "root", name="marker:1", root_kind="marker", matrix_words=A,
              select=True),
        event(4, "push", depth=1, base_words=I),
    ]}
    expect_error(ambiguous, "ambiguous base matrix")

    bad_pop = valid_fixture()
    bad_pop["events"][6] = event(7, "pop", depth=2, restored_words=C)
    expect_error(bad_pop, "did not restore")

    no_commit = {"events": [
        event(1, "root", name="object", root_kind="object_root", matrix_words=I),
        event(2, "submit", destination="missing", oba="0x009e0001"),
    ]}
    expect_error(no_commit, "no prior commit")
    print("PASS: exact stack lineage, siblings, deep chain, markers, visibility, ambiguity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
