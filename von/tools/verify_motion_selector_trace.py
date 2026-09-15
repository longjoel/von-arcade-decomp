#!/usr/bin/env python3
"""Verify Lua-captured object selector/cursor records against motion tables."""
import argparse
import json
import re
from pathlib import Path

LINE = re.compile(
    r"motion-selector: frame=(\d+) object=([0-9a-f]+)(?: g0=([0-9a-f]+))? header=([0-9a-f]+)(?: body_header=([0-9a-f]+))? "
    r"sel=([0-9a-f]+) state=([0-9a-f]+) frame_cursor=([0-9a-f]+)", re.I)


def parse(path: Path):
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = LINE.fullmatch(line)
        if match:
            frame, obj, g0, header, body_header, selector, state, cursor = match.groups()
            records.append({
                "frame": int(frame), "object": int(obj, 16),
                "g0": int(g0, 16) if g0 else None,
                "header": int(header, 16), "selector": int(selector, 16),
                "body_header": int(body_header, 16) if body_header else None,
                "state": int(state, 16), "cursor": int(cursor, 16),
            })
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--motion", required=True, type=Path)
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--table", required=True, type=int)
    parser.add_argument("--body-table", type=int,
                        help="require the paired body header from this table")
    parser.add_argument("--object", type=lambda value: int(value, 0))
    parser.add_argument("--prefix", type=int, default=0,
                        help="required cursor sequence length, starting at one")
    args = parser.parse_args()

    clips = json.loads(args.motion.read_text(encoding="utf-8"))["clips"]
    if not 0 <= args.table < len(clips):
        raise SystemExit(f"table {args.table} is outside motion inventory")
    header = clips[args.table]["header"]
    records = [record for record in parse(args.log) if record["header"] == header]
    if args.object is not None:
        records = [record for record in records if record["object"] == args.object]
    if not records:
        raise SystemExit(f"no selector records for table {args.table} header={header:08x}")

    if args.body_table is not None:
        if not 0 <= args.body_table < len(clips):
            raise SystemExit(f"body table {args.body_table} is outside motion inventory")
        body_header = clips[args.body_table]["header"]
        actual = {record["body_header"] for record in records}
        if actual != {body_header}:
            got = ", ".join("none" if value is None else f"{value:08x}"
                            for value in sorted(actual, key=lambda value: value is None))
            raise SystemExit(f"body headers {{{got}}}, want {body_header:08x}")

    if args.prefix:
        expected = list(range(1, args.prefix + 1))
        actual = [record["cursor"] for record in records[:args.prefix]]
        if actual != expected:
            raise SystemExit(f"cursor prefix {actual!r}, want {expected!r}")
    pair = f" body-table={args.body_table}" if args.body_table is not None else ""
    print(f"PASS: table={args.table}{pair} header={header:08x} "
          f"records={len(records)} cursor-prefix={args.prefix}")


if __name__ == "__main__":
    main()
