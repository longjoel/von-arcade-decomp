#!/usr/bin/env python3
"""Dump polygon-ROM object windows referenced by a MAME geometry trace."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


OBJECT = re.compile(
    r"vonj_geometry_object: (?:seq=\d+ )?(?:time=[0-9.e+-]+ )?"
    r"tpa=([0-9a-f]+) tha=([0-9a-f]+) "
    r"oba=([0-9a-f]+) count=([0-9a-f]+) mode=(\d+) source=([a-z-]+)"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path,
                        default=Path("von/build/disasm/vonj-geometry-select.trace"))
    parser.add_argument("--rom", type=Path,
                        default=Path("von/build/disasm/geometry-rom.bin"))
    parser.add_argument("--output-dir", type=Path,
                        default=Path("von/build/disasm/geometry-objects"))
    parser.add_argument("--window", type=int, default=0x1000)
    parser.add_argument("--limit", type=int, default=128)
    args = parser.parse_args()

    rom = args.rom.read_bytes()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    seen: set[int] = set()
    rows: list[tuple[str, int, int, int, int, int, str]] = []
    for match in OBJECT.finditer(args.trace.read_text()):
        tpa, tha, oba, count, mode, source = match.groups()
        tpa_i, tha_i, oba_i, count_i, mode_i = (
            int(tpa, 16), int(tha, 16), int(oba, 16), int(count, 16), int(mode)
        )
        if source != "polygon-rom":
            continue
        index = oba_i & 0x3fffff
        if index in seen:
            continue
        seen.add(index)
        words = min(count_i or args.window, args.window)
        start = index * 4
        end = min(start + words * 4, len(rom))
        values = [int.from_bytes(rom[pos:pos + 4], "little")
                  for pos in range(start, end, 4)]
        name = f"{len(rows):03d}-oba{oba_i:08x}-tpa{tpa_i:08x}-tha{tha_i:08x}.hex"
        (args.output_dir / name).write_text(
            f"# oba={oba_i:08x} index={index:06x} tpa={tpa_i:08x} "
            f"tha={tha_i:08x} count={count_i:08x} mode={mode_i}\n" +
            "\n".join(f"{offset:04x} {value:08x}"
                       for offset, value in enumerate(values)) + "\n"
        )
        rows.append((name, oba_i, tpa_i, tha_i, count_i, mode_i, source))
        if len(rows) >= args.limit:
            break

    (args.output_dir / "index.tsv").write_text(
        "file\toba\ttpa\ttha\tcount\tmode\tsource\n" +
        "\n".join(
            f"{name}\t0x{oba:08x}\t0x{tpa:08x}\t0x{tha:08x}\t"
            f"0x{count:08x}\t{mode}\t{source}"
            for name, oba, tpa, tha, count, mode, source in rows
        ) + "\n")
    print(f"dumped {len(rows)} polygon-ROM objects to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
