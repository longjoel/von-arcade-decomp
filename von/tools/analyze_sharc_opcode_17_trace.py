#!/usr/bin/env python3
"""Summarize paired opcode-0x17/helper-0x20de1 trace entries."""

from __future__ import annotations

import argparse
import re
import struct
from pathlib import Path


ENTRY = "vonj_sharc_20de1_step: pc=020de1 "
NORMAL = "vonj_sharc_20de1_step: pc=020e4c "
SENTINEL = "vonj_sharc_20de1_step: pc=020e50 "


def float_word(word: str) -> float:
    return struct.unpack(">f", bytes.fromhex(word))[0]


def summarize(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if ENTRY in line:
            values = dict(re.findall(r"(f\d+|dm\d+)=([0-9a-f]+)", line))
            current = {
                "entry_f0": float_word(values["f0"]),
                "entry_f1": float_word(values["f1"]),
                "entry_f4": float_word(values["f4"]),
                "entry_f5": float_word(values["f5"]),
                "entry_f8": float_word(values["f8"]),
                "entry_f9": float_word(values["f9"]),
                "entry_dm": tuple(values[f"dm{i}"] for i in range(9)),
                "return": None,
                "return_pc": None,
            }
            rows.append(current)
        elif current is not None and NORMAL in line:
            values = dict(re.findall(r"(f\d+)=([0-9a-f]+)", line))
            current["return"] = float_word(values["f0"])
            current["return_pc"] = "020e4c"
        elif current is not None and SENTINEL in line:
            current["return"] = -0.1
            current["return_pc"] = "020e50"
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    args = parser.parse_args()
    rows = summarize(args.trace)
    paired = [row for row in rows if row["return_pc"] is not None]
    normal = [row for row in paired if row["return_pc"] == "020e4c"]
    zero = [row for row in normal if row["return"] == 0.0]
    print(f"helper entries: {len(rows)}")
    print(f"paired returns: {len(paired)}")
    print(f"normal returns: {len(normal)}")
    print(f"normal exact-zero returns: {len(zero)}")
    print(f"sentinel returns: {sum(row['return_pc'] == '020e50' for row in paired)}")
    for index, row in enumerate(paired, 1):
        print(
            f"{index:02d} pc={row['return_pc']} result={row['return']:.9g} "
            f"entry_f5={row['entry_f5']:.9g} "
            f"entry_f8={row['entry_f8']:.9g} entry_f9={row['entry_f9']:.9g}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
