#!/usr/bin/env python3
"""Validate the profile-indexed texture setup at i960 0x281f0."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_texture_profile_setup_281f0.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "profile_word", "saved_profile_address", "source_address",
        "primary_destination", "secondary_destination", "decoder_status",
        "state_a", "state_b", "saved_state_a", "saved_state_b")]


def main() -> int:
    listing = LISTING.read_text(encoding="utf-8")
    for address, fragment in (
        ("281f0", "ld\t0x280c0[g0*4],g4"),
        ("2820c", "st\tg4,0x512bd0"),
        ("28218", "call\t0x27e50"),
        ("2821c", "cmpibne\t1,g0,0x28230"),
        ("28224", "st\tg3,0x503a00"),
        ("28230", "cmpibne\t2,g0,0x28268"),
        ("28248", "st\tg3,0x5039f4"),
        ("28250", "st\tg14,0x503a00"),
        ("28258", "st\tg4,0x503a0c"),
        ("28260", "st\tg5,0x503a10"),
    ):
        line = next((line for line in listing.splitlines()
                     if f"{address}:" in line), "")
        if fragment not in line:
            raise SystemExit(f"0x281f0 instruction {address} missing {fragment}")

    with tempfile.TemporaryDirectory(prefix="von-texture-profile-281f0-") as directory:
        library = Path(directory) / "profile.so"
        subprocess.run([
            os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
            str(SOURCE), "-o", str(library)], check=True)
        recovered = ctypes.CDLL(str(library))
        function = recovered.recovered_texture_profile_setup_281f0
        function.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                             ctypes.c_uint32, ctypes.c_uint32,
                             ctypes.POINTER(Plan)]
        function.restype = None

        table_word = recovered.recovered_texture_profile_table_word_281f0
        table_word.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
        table_word.restype = ctypes.c_uint32
        expected_table = (0x02C77438, 0x02CDBAD3, 0x02D594A1,
                          0x02DDEFFC, 0x02E55C42)
        for index, expected_word in enumerate(expected_table):
            word = ctypes.c_uint32()
            if table_word(index, ctypes.byref(word)) != 1 or word.value != expected_word:
                raise SystemExit(f"0x280c0 profile table mismatch at index {index}")
        word = ctypes.c_uint32()
        if table_word(5, ctypes.byref(word)) != 0:
            raise SystemExit("0x280c0 bounded table view accepted index 5")

        vectors = (
            (0x00123456, 0, 7, 8, (0x00123456, 0x00123456, 0x00123456,
                                  0x11200000, 0x11000000, 0, 7, 8, 0, 0)),
            (0x02C77438, 1, 7, 8, (0x02C77438, 0x02C77438, 0x02C77438,
                                  0x11200000, 0x11000000, 1, 7, 29, 0, 0)),
            (0x02C00008, 2, 0x11111111, 0x22222222,
             (0x02C00008, 0x02C00008, 0x02C00008, 0x11200000,
              0x11000000, 2, 5, 0, 0x11111111, 0x22222222)),
            (0xFFFFFFFF, 9, 3, 4, (0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
                                  0x11200000, 0x11000000, 9, 3, 4, 0, 0)),
        )
        for profile_word, status, prior_a, prior_b, expected in vectors:
            result = Plan()
            function(profile_word, status, prior_a, prior_b, ctypes.byref(result))
            actual = tuple(getattr(result, name) for name, _ in Plan._fields_)
            if actual != expected:
                raise SystemExit(f"0x281f0 mismatch: {actual!r} != {expected!r}")

    print(f"PASS: {len(vectors)} texture profile setup vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
