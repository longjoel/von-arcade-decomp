#!/usr/bin/env python3
"""Verify the main-CPU caller packet for SHARC opcode 0x09."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


def main() -> int:
    lines = LISTING.read_text(encoding="utf-8").splitlines()
    text = "\n".join(lines)
    required = (
        "41fbc:"
        , "mov\t5,g2"
        , "41fc8:"
        , "mov\t9,g2"
        , "ldq\t0x8(r4),g4"
        , "stq\tg4,0x884000"
        , "ldq\t0x18(r4),g4"
        , "stq\tg4,0x884010"
        , "ldq\t0x28(r4),g4"
        , "stq\tg4,0x884020"
        , "41f8c:"
        , "addo\t31,27,r7"
        , "42040:"
        , "st\tr7,0x884000"
        , "42094:"
        , "mov\t6,g2"
        , "420c4:"
        , "st\tg2,0x884000"
    )
    for fragment in required:
        if fragment not in text:
            raise SystemExit(f"main-CPU opcode-0x09 caller missing {fragment}")

    window = text[text.index("41fbc:"):text.index("42000:")]
    if window.index("mov\t5,g2") > window.index("mov\t9,g2"):
        raise SystemExit("opcode 0x05 must precede opcode 0x09")
    if window.count("stq\tg4,0x884000") != 1:
        raise SystemExit("first opcode-0x09 quadword destination is missing")
    if window.count("stq\tg4,0x884010") != 1:
        raise SystemExit("second opcode-0x09 quadword destination is missing")
    if window.count("stq\tg4,0x884020") != 1:
        raise SystemExit("third opcode-0x09 quadword destination is missing")

    # The neighboring opcode-0x07 paths reuse the same three object lanes.
    # This is a field-layout invariant independent of the later transform.
    for start, end in (("420e4:", "42198:"), ("421cc:", "42290:")):
        path = text[text.index(start):text.index(end)]
        if path.count("ldq\t0x8(r4),g4") != 1:
            raise SystemExit(f"{start} missing first four-word object lane")
        if path.count("ldq\t0x18(r4),g4") != 1:
            raise SystemExit(f"{start} missing second four-word object lane")
        if path.count("ldq\t0x28(r4),g4") != 1:
            raise SystemExit(f"{start} missing third four-word object lane")
        if "stq\tg4,0x884000" not in path or "stq\tg4,0x884010" not in path:
            raise SystemExit(f"{start} missing opcode-0x07 lane destinations")
        if "stq\tg4,0x884020" not in path:
            raise SystemExit(f"{start} missing third opcode-0x07 lane destination")

    # Two object constructors fill the same twelve-word region from the
    # SHARC state-readback request (FIFO command value 17).
    for start, end in (("3f600:", "3f6d4:"), ("3f6e0:", "3f7c8:")):
        constructor = text[text.index(start):text.index(end)]
        if "mov\t17,g7" not in constructor:
            raise SystemExit(f"{start} missing state-readback request")
        for offset in range(0x08, 0x38, 4):
            if f"st\tg7,0x{offset:x}(g5)" not in constructor:
                raise SystemExit(f"{start} missing twelve-word store at +0x{offset:x}")

    continuation = text[text.index("41f8c:"):text.index("420d0:")]
    if "addo\t31,27,r7" not in continuation:
        raise SystemExit("opcode-0x3a command value setup is missing")
    if continuation.index("st\tr7,0x884000") > continuation.index("mov\t6,g2"):
        raise SystemExit("opcode-0x3a command must precede opcode 0x06")
    if continuation.index("st\tg2,0x884000") > continuation.index("mov\t6,g2"):
        raise SystemExit("opcode 0x06 write is missing")

    print("PASS: main-CPU opcode-0x09 caller packet and 0x3a/0x06 continuation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
