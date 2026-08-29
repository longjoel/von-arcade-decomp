#!/usr/bin/env python3
"""Summarize an i960 attract PC-coverage dump against the raw listing."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


INSTRUCTION_RE = re.compile(r"^\s*([0-9a-fA-F]+):")
CALL_RE = re.compile(r"\b(?:call|bal)\s+0x([0-9a-fA-F]+)")


def load_pcs(path: Path) -> set[int]:
    pcs: set[int] = set()
    for line in path.read_text(encoding="ascii").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            pcs.add(int(line, 16))
    return pcs


def contiguous_ranges(pcs: set[int]) -> list[tuple[int, int]]:
    if not pcs:
        return []
    ranges: list[tuple[int, int]] = []
    start = previous = min(pcs)
    for pc in sorted(pcs)[1:]:
        if pc != previous + 4:
            ranges.append((start, previous + 4))
            start = pc
        previous = pc
    ranges.append((start, previous + 4))
    return ranges


def listing_data(path: Path) -> tuple[set[int], dict[int, set[int]]]:
    instructions: set[int] = set()
    callers: dict[int, set[int]] = {}
    for line in path.read_text(encoding="ascii", errors="replace").splitlines():
        instruction = INSTRUCTION_RE.match(line)
        if not instruction or "\t.word" in line:
            continue
        pc = int(instruction.group(1), 16)
        instructions.add(pc)
        target = CALL_RE.search(line)
        if target:
            callers.setdefault(int(target.group(1), 16), set()).add(pc)
    return instructions, callers


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pcs", required=True, type=Path)
    parser.add_argument("--listing", required=True, type=Path)
    parser.add_argument("--json", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    args = parser.parse_args()

    pcs = load_pcs(args.pcs)
    instructions, callers = listing_data(args.listing)
    visited = pcs & instructions
    unknown = pcs - instructions
    executed_edges = sorted(
        (caller, target)
        for target, target_callers in callers.items()
        if target in visited
        for caller in target_callers
        if caller in visited
    )
    executed_targets = sorted({target for _, target in executed_edges})
    ranges = contiguous_ranges(visited)
    report = {
        "schema_version": 1,
        "pc_log": str(args.pcs),
        "visited_instruction_count": len(visited),
        "visited_instruction_bytes": len(visited) * 4,
        "visited_contiguous_ranges": len(ranges),
        "known_direct_call_targets": len(callers),
        "visited_direct_call_targets": len(executed_targets),
        "visited_direct_call_edges": len(executed_edges),
        "unknown_pc_count": len(unknown),
        "minimum_pc": f"0x{min(visited):08x}" if visited else None,
        "maximum_pc": f"0x{max(visited):08x}" if visited else None,
        "executed_direct_targets": [f"0x{target:08x}" for target in executed_targets],
        "executed_direct_edges": [
            {"caller": f"0x{caller:08x}", "target": f"0x{target:08x}"}
            for caller, target in executed_edges
        ],
        "ranges": [
            {"start": f"0x{start:08x}", "end": f"0x{end:08x}", "bytes": end - start}
            for start, end in ranges
        ],
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown = (
        "# i960 Attract Coverage\n\n"
        f"- Visited instructions: {len(visited):,} ({len(visited) * 4:,} bytes)\n"
        f"- Visited direct call targets: {len(executed_targets):,} / {len(callers):,}\n"
        f"- Visited direct call edges: {len(executed_edges):,}\n"
        f"- Contiguous visited ranges: {len(ranges):,}\n"
        f"- PCs absent from decoded listing: {len(unknown):,}\n"
        f"- Observed ROM span: {report['minimum_pc']}–{report['maximum_pc']}\n"
    )
    args.markdown.write_text(markdown, encoding="utf-8")
    print(markdown, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
