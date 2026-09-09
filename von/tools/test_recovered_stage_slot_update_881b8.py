#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Table(ctypes.Structure):
    _fields_ = [("words", (ctypes.c_uint32 * 3) * 120)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-stage-slot-update-") as d:
        so = Path(d) / "stage-slot-update.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        str(ROOT / "von/i960/recovered_stage_slot_update_881b8.c"),
                        "-o", str(so)], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_stage_slot_update_881b8
        fn.argtypes = [ctypes.POINTER(Table), ctypes.c_uint32,
                       ctypes.c_uint32, ctypes.c_uint32]
        state = Table()
        ctypes.memset(ctypes.byref(state), 0xa5, ctypes.sizeof(state))
        fn(ctypes.byref(state), 0, 0x11223344, 0x55667788)
        fn(ctypes.byref(state), 120 + 7, 0x99aabbcc, 0xddeeff00)
        assert tuple(state.words[0]) == (0xa5a5a5a5, 0x11223344, 0x55667788)
        assert tuple(state.words[7]) == (0xa5a5a5a5, 0x99aabbcc, 0xddeeff00)
        assert tuple(state.words[8]) == (0xa5a5a5a5,) * 3
        assert tuple(state.words[119]) == (0xa5a5a5a5,) * 3
        print("PASS: stage slot update modulo-120 publication")


if __name__ == "__main__":
    main()
