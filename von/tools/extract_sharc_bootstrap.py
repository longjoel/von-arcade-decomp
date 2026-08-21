#!/usr/bin/env python3
"""Extract the host-uploaded SHARC bootstrap from the assembled i960 image."""

from __future__ import annotations

import argparse
from pathlib import Path


SOURCE_OFFSET = 0x16B58C
WORD_COUNT = 0x2B1E
WORD_SIZE = 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).parents[1] / "build/disasm/vonj-maincpu.bin",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parents[1] / "build/disasm/vonj-sharc-bootstrap.bin",
    )
    args = parser.parse_args()

    image = args.input.read_bytes()
    end = SOURCE_OFFSET + WORD_COUNT * WORD_SIZE
    if end > len(image):
        raise SystemExit(
            f"input is too short: need 0x{end:x} bytes, found 0x{len(image):x}"
        )

    payload = image[SOURCE_OFFSET:end]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(
        f"Wrote {WORD_COUNT} 16-bit words ({len(payload):#x} bytes) "
        f"from maincpu+0x{SOURCE_OFFSET:08x} to {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
