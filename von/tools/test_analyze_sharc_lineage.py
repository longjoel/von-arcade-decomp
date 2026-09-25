#!/usr/bin/env python3
"""Synthetic gates for exact-state SHARC lineage recovery."""

from analyze_sharc_lineage import analyze


I = [0x3F800000, 0, 0, 0, 0x3F800000, 0, 0, 0, 0x3F800000, 0, 0, 0]
R = I[:9] + [0x40000000, 0, 0]


def program(push, commit, pop, depth=1, oba="0x1"):
    return {"push": {"event_id": push, "depth": depth,
                      "base_words": I},
            "commit": {"event_id": commit, "depth": depth,
                        "matrix_words": R, "stack_words": R, "oba": oba},
            "pop": {"event_id": pop, "depth": depth,
                    "restored_words": I}}


def main():
    # One live exact-state parent is promoted; no spatial/pivot information is
    # present anywhere in this fixture.
    parent = program(1, 2, 10)
    child = program(3, 4, 9, depth=2, oba="0x2")
    child["push"]["base_words"] = R
    result = analyze({"part_programs": [parent, child]})
    assert result["validation"]["ambiguous"] == 0
    assert result["parts"][1]["parent_program"] == 0

    # Two identical live matrices at the required depth must fail promotion,
    # even when one happens to be temporally nearer.
    left = program(1, 2, 20, oba="0x10")
    right = program(3, 4, 20, oba="0x11")
    ambiguous_child = program(5, 6, 19, depth=2, oba="0x12")
    ambiguous_child["push"]["base_words"] = R
    result = analyze({"part_programs": [left, right, ambiguous_child]})
    assert result["validation"]["ambiguous"] == 1
    assert result["parts"][2]["parent_kind"] == "ambiguous"

    # A body-stream packet at a nested stack level may have an absolute record
    # but still inherits a live marker matrix.  The stream name alone must not
    # promote it to an object root.
    nested_body = program(3, 4, 9, depth=3, oba="0x20")
    nested_body["push"]["source_stream"] = "body"
    nested_body["commit"]["source_stream"] = "body"
    result = analyze({"part_programs": [nested_body]})
    assert result["parts"][0]["parent_kind"] == "marker_or_root"
    print("PASS: exact-state lineage uniqueness and ambiguity gate")


if __name__ == "__main__":
    main()
