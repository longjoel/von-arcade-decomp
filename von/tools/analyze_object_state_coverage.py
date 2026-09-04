#!/usr/bin/env python3
"""Summarize visited state arms for the i960 object-state helper."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


STATE_ENTRIES = {
    0: 0x000790A4,
    1: 0x00079178,
    2: 0x000791FC,
    3: 0x0007928C,
    4: 0x00079374,
    5: 0x00079400,
    6: 0x000794AC,
    7: 0x0007953C,
    8: 0x000795A8,
    9: 0x000795B8,
}


def read_pcs(path: Path) -> set[int]:
    pcs = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        value = line.strip()
        if value and all(character in "0123456789abcdefABCDEF" for character in value):
            pcs.add(int(value, 16))
    return pcs


def analyze(pcs: set[int]) -> dict[str, object]:
    visited = [state for state, entry in STATE_ENTRIES.items() if entry in pcs]
    return {
        "helper": {"start": "0x00079050", "end": "0x00079630"},
        "visited_states": visited,
        "unvisited_states": [state for state in STATE_ENTRIES if state not in visited],
        "state_entries": {
            str(state): {
                "entry": f"0x{entry:08x}",
                "visited": entry in pcs,
            }
            for state, entry in STATE_ENTRIES.items()
        },
    }


def path_error(label: str, path: Path, root: Path, *, output: bool = False) -> str | None:
    if path.is_symlink():
        return f"{label} path must not be a symlink: {path}"
    try:
        path.resolve().relative_to(root.resolve())
    except (OSError, RuntimeError, ValueError):
        return f"{label} path escapes root: {path}"
    if not output and not path.is_file():
        return f"missing {label}: {path}"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pcs", type=Path)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd(),
                        help="root that coverage input and output must remain within")
    args = parser.parse_args()

    root = args.root.resolve()
    for label, path, output in (("PC log", args.pcs, False), ("JSON output", args.json, True)):
        if path is None:
            continue
        error = path_error(label, path, root, output=output)
        if error:
            print(f"Object-state coverage: {error}")
            return 1

    report = analyze(read_pcs(args.pcs))
    if args.json:
        args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"helper: {report['helper']['start']}..{report['helper']['end']}")
    print("visited states: " + ", ".join(map(str, report["visited_states"])))
    print("unvisited states: " + ", ".join(map(str, report["unvisited_states"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
