#!/usr/bin/env python3
"""Recover parentage from exact SHARC stack state.

This intentionally has no geometric or fitted-pivot fallback.  A child push
may inherit a previously committed matrix only when the complete 12-word
state matches and the candidate was live at the child's push.  Ties are
reported as ambiguity so a contract cannot be promoted silently.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


class LineageError(ValueError):
    pass


def _interval(program: dict) -> tuple[int, int]:
    push = program["push"]["event_id"]
    pop = program.get("pop", {}).get("event_id", 2**63 - 1)
    return push, pop


def analyze(document: dict) -> dict:
    programs = list(document.get("part_programs", []))
    programs.sort(key=lambda p: p["push"]["event_id"])
    by_matrix: dict[tuple[int, ...], list[int]] = {}
    for index, program in enumerate(programs):
        commit = program["commit"]
        key = tuple(commit.get("stack_words", commit["matrix_words"]))
        by_matrix.setdefault(key, []).append(index)

    parts = []
    ambiguities = []
    for index, program in enumerate(programs):
        push = program["push"]
        base = tuple(push["base_words"])
        child_event = push["event_id"]
        child_depth = push["depth"]
        candidates = []
        for candidate in by_matrix.get(base, []):
            if candidate == index:
                continue
            parent = programs[candidate]
            ppush, ppop = _interval(parent)
            if ppush < child_event < ppop:
                # A normal push copies the immediately previous stack level.
                # Keep the depth constraint strict; equal matrices at another
                # level are not lineage evidence.
                if parent["commit"]["depth"] == child_depth - 1:
                    candidates.append(candidate)
        if len(candidates) == 1:
            parent_kind = "part"
            parent_index = candidates[0]
            parent_oba = programs[parent_index]["commit"].get("oba")
        elif len(candidates) > 1:
            parent_kind = "ambiguous"
            parent_index = None
            parent_oba = None
            ambiguities.append({"program": index, "event_id": child_event,
                                "candidates": candidates})
        else:
            # No prior committed matrix means this branch enters from the
            # object/root or a marker slot.  Do not guess which one: retain a
            # named unresolved source for contract review.
            # Stream type does not establish rootage.  In particular, the
            # Temjin body emitter runs at depth 3 immediately after marker
            # writes, so its packets cannot be promoted to direct object-root
            # edges just because the body records are absolute.  A direct
            # root is only evidenced at depth 1; deeper unmatched pushes wait
            # for a named marker/root source.
            parent_kind = "object_root" if child_depth <= 1 else "marker_or_root"
            parent_index = None
            parent_oba = None
        packet_oba = program["commit"].get("oba")
        parts.append({
            "program": index,
            "oba": packet_oba,
            "push_event_id": child_event,
            "depth": child_depth,
            "parent_kind": parent_kind,
            "parent_program": parent_index,
            "parent_oba": parent_oba,
            "base_words": list(base),
        })

    unresolved = sum(part["parent_kind"] in ("marker_or_root", "object_root")
                     for part in parts)
    return {
        "schema_version": 1,
        "lineage_policy": "exact-stack-state-v1",
        "parts": parts,
        "ambiguities": ambiguities,
        "validation": {"ambiguous": len(ambiguities),
                        "unresolved": unresolved, "parts": len(parts)},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true",
                        help="fail if any exact-state parent is ambiguous")
    args = parser.parse_args()
    result = analyze(json.loads(args.fixture.read_text()))
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result["validation"], sort_keys=True,
                     separators=(",", ":")))
    if args.check and (result["ambiguities"] or result["validation"]["unresolved"]):
        raise SystemExit("SHARC lineage is not fully resolved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
