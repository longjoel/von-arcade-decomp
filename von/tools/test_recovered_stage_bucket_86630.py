#!/usr/bin/env python3
import ctypes
import os
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


def main():
    listing = LISTING.read_text()
    for instruction in (r"86650:.*remi.*6",
                        r"86658:.*ld.*0x86664",
                        r"866a0:.*divi.*6",
                        r"866a4:.*ldob.*0x842a0"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory(prefix="von-stage-bucket-") as d:
        so = Path(d) / "stage-bucket.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        str(ROOT / "von/i960/recovered_stage_bucket_86630.c"),
                        "-o", str(so)], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_stage_bucket_86630
        fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8),
                       ctypes.c_uint32]
        fn.restype = ctypes.c_uint32
        rom = lib.recovered_stage_bucket_86630_rom
        rom.argtypes = [ctypes.c_uint32]
        rom.restype = ctypes.c_uint32
        table = (ctypes.c_uint8 * 8)(10, 11, 12, 13, 14, 15, 16, 17)
        assert fn(0, table, 8) == 10
        assert fn(1, table, 8) == 11
        assert fn(2, table, 8) == 4
        assert fn(3, table, 8) == 4
        assert fn(4, table, 8) == 4
        assert fn(5, table, 8) == 3
        assert fn(6, table, 8) == 11
        assert fn(7, table, 8) == 12
        assert fn(0, table, 0) == 0
        assert fn(60, table, 2) == 0, "bounded table adapter"
        assert [rom(value) for value in range(8)] == [6, 2, 4, 4, 4, 3, 2, 5]
        assert [rom(value) for value in (12, 18, 24, 30, 36)] == [5, 1, 1, 5, 1]
        print("PASS: stage bucket residue and table dispatch")


if __name__ == "__main__":
    main()
