#!/usr/bin/env python3
"""Verify the recovered geometry buffer and four-batch submission shape."""

from __future__ import annotations

import argparse
from pathlib import Path

from verify_geometry_buffer import expected, load_dump


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dump", type=Path)
    args = parser.parse_args()
    values = load_dump(args.dump)
    if values != expected():
        print("buffer mismatch")
        return 1

    batch_words = 0x800
    for batch in range(4):
        start = batch * batch_words
        end = start + batch_words
        if len(values[start:end]) != batch_words:
            print(f"batch {batch}: incorrect length")
            return 1
        print(
            f"batch {batch}: source_offset=0x{batch * 0x2000:04x} "
            f"command_offset=0x{batch * 0x800:04x} "
            f"command_word=0x1414 count=0x800"
        )
    print("chain match: buffer, four batches, and command strides")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
