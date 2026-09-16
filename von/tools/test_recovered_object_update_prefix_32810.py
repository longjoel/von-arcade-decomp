#!/usr/bin/env python3
"""Validate the 0x32810 prefix range helper and listing evidence."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_object_update_prefix_32810.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "prefix-32810.so"
    subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                    "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
    dll = ctypes.CDLL(str(library))
    rng = dll.recovered_object_update_prefix_32810_range
    rng.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    rng.restype = ctypes.c_uint32
    # value = (0x9ff + delta - facing) & 0xffff; 1 when > 0x13fe.
    assert rng(0, 0) == 0                      # 0x9ff
    assert rng(0x1000, 0) == 1                 # 0x19ff > 0x13fe
    assert rng(0, 0x9ff) == 0                  # 0
    assert rng(0x8000, 0) == 1                 # sign-extends to 0x89ff

    listing = LISTING.read_text(encoding="utf-8")
    block = listing[listing.index("   32818:"):listing.index("   32928:")]
    for evidence in (
            "ld\t0x74(g0),r9", "st\tr10,0xa4(g0)", "st\tr11,0xa8(g0)",
            "mov\t31,r10", "st\tr11,0x7c(g0)", "mov\t10,r10",
            "stos\tg4,0x84(g0)", "st\tg4,0x80(g0)",
            "lda\t0x13fe,r11", "stos\tg7,0x86(g0)", "stos\tr10,0x1fc(g0)"):
        if evidence not in block:
            raise AssertionError(f"prefix listing evidence missing: {evidence}")

print("PASS: 0x32810 object-update prefix")
