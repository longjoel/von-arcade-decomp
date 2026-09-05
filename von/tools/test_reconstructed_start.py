#!/usr/bin/env python3
"""Check the bounded i960 startup register/stack setup contract."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/start_reconstructed.s"


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8")
    required = (
        ".globl _start_ip",
        "_start_ip:",
        "lda 0x00500400,fp",
        "lda -0x40(fp),pfp",
        "lda 0x40(fp),sp",
        "mov 0,g14",
        "call _i960_reconstructed_main",
        "b _start_ip",
    )
    missing = [fragment for fragment in required if fragment not in text]
    if missing:
        raise SystemExit("startup contract missing: " + ", ".join(missing))
    print("PASS: reconstructed i960 startup register/stack setup contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
