#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [
        ("loader_index", ctypes.c_uint32), ("loader_address", ctypes.c_uint32),
        ("source_base", ctypes.c_uint32), ("source_word_count_immediate", ctypes.c_uint32),
        ("copied_halfword_count", ctypes.c_uint32), ("copied_byte_count", ctypes.c_uint32),
        ("source_publication_address", ctypes.c_uint32), ("destination_address", ctypes.c_uint32),
        ("selected_source_address", ctypes.c_uint32), ("reset_copy_helper", ctypes.c_uint32),
        ("return_target", ctypes.c_uint32),
    ]


def main():
    with tempfile.TemporaryDirectory(prefix="von-rom-bank-loaders-") as d:
        so = Path(d) / "rom-bank-loaders.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_runtime_rom_bank_loaders_eb5b0.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_runtime_rom_bank_loader_eb5b0
        fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        bases = [0x5e0000, 0x5c0000, 0x5a0000, 0x580000,
                 0x560000, 0x540000, 0x520000, 0x502000]
        for index, base in enumerate(bases):
            out = Result()
            assert fn(index, ctypes.byref(out)) == 1
            immediate = 0xefff if index == 7 else 0xffff
            assert (out.loader_index, out.loader_address, out.source_base,
                    out.source_word_count_immediate, out.copied_halfword_count,
                    out.copied_byte_count, out.source_publication_address,
                    out.destination_address, out.selected_source_address,
                    out.reset_copy_helper) == (
                index, 0xeb5b0 + index * 0x50, base, immediate, immediate + 1,
                (immediate + 1) * 2, 0x501cc0, 0x501cc4, 0x501cc4, 0xeb510)
        out = Result()
        assert fn(8, ctypes.byref(out)) == 0
        assert out.return_target == 0
        print("PASS: 0xeb5b0-0xeb7e0 ROM-bank loaders")


if __name__ == "__main__":
    main()
