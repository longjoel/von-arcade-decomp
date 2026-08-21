#!/usr/bin/env python3
"""List i960 disassembly references into the documented Model 2 address map."""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path


LINE_RE = re.compile(r"^\s*([0-9a-fA-F]+):")
VALUE_RE = re.compile(r"0x([0-9a-fA-F]+)")
REGIONS = (
    ("host_ram", 0x00500000, 0x00600000),
    ("geo_fifo", 0x00800000, 0x00804000),
    ("geo_program", 0x00804000, 0x00808000),
    ("copro_function", 0x00880000, 0x00884000),
    ("copro_fifo", 0x00884000, 0x00888000),
    ("copro_control", 0x00980000, 0x00980024),
    ("comm_ram", 0x01A00000, 0x01A04000),
    ("io_registers", 0x01C00000, 0x01C00220),
    ("backup_sram", 0x01D00000, 0x01D04000),
    ("main_data", 0x02000000, 0x04000000),
    ("extra_data", 0x06000000, 0x07000000),
    ("texture_ram", 0x11000000, 0x11400000),
)


def region_for(value: int) -> str | None:
    for name, start, end in REGIONS:
        if start <= value < end:
            return name
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--listing", type=Path, default=Path(__file__).parents[1] / "build/disasm/vonj-maincpu.lst")
    parser.add_argument("--all", action="store_true", help="print every reference instead of a compact sample")
    args = parser.parse_args()

    references: dict[str, dict[int, list[str]]] = defaultdict(lambda: defaultdict(list))
    for line in args.listing.read_text(encoding="ascii").splitlines():
        if "\t.word" in line:
            continue
        pc_match = LINE_RE.match(line)
        if not pc_match:
            continue
        pc = int(pc_match.group(1), 16)
        for value_match in VALUE_RE.finditer(line):
            value = int(value_match.group(1), 16)
            region = region_for(value)
            if region is not None:
                references[region][pc].append(f"0x{value:08x}")

    for region, pcs in references.items():
        print(f"[{region}] {len(pcs)} instruction sites")
        sites = sorted(pcs)
        if not args.all and len(sites) > 40:
            sites = sites[:20] + sites[-20:]
        for pc in sites:
            values = ", ".join(dict.fromkeys(pcs[pc]))
            print(f"  0x{pc:08x}: {values}")
        if not args.all and len(pcs) > 40:
            print(f"  ... {len(pcs) - 40} sites omitted; use --all")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
