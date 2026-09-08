#!/usr/bin/env python3
"""Validate the profile-word equality predicate at i960 0x28270."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_texture_profile_match_28270.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


def main() -> int:
    listing = LISTING.read_text(encoding="utf-8")
    for address, fragment in (
        ("28280", "ld\t0x280c0[g0*4],g5"),
        ("28288", "ld\t0x512bd0,g4"),
        ("28290", "cmpibe\tg4,g5,0x2829c"),
        ("28294", "mov\t1,g0"),
        ("2829c", "mov\t0,g0"),
    ):
        line = next((line for line in listing.splitlines()
                     if f"{address}:" in line), "")
        if fragment not in line:
            raise SystemExit(f"0x28270 instruction {address} missing {fragment}")

    with tempfile.TemporaryDirectory(prefix="von-texture-profile-match-") as directory:
        library = Path(directory) / "profile-match.so"
        subprocess.run([
            os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
            str(SOURCE), "-o", str(library)], check=True)
        recovered = ctypes.CDLL(str(library))
        match = recovered.recovered_texture_profile_match_28270
        match.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        match.restype = ctypes.c_uint32
        for table_word, published, expected in (
            (0, 0, 1),
            (0x02C77438, 0x02C77438, 1),
            (0x02C77438, 0x02C00008, 0),
            (0xFFFFFFFF, 0, 0),
        ):
            actual = match(table_word, published)
            if actual != expected:
                raise SystemExit(
                    f"profile match mismatch: {table_word:#x}, {published:#x} "
                    f"=> {actual}, expected {expected}"
                )

    print("PASS: 4 texture profile match vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
