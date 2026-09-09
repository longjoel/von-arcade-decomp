#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class State(ctypes.Structure):
    _fields_ = [("object_table_200", ctypes.c_uint8 * 32),
                ("global_576ba0", ctypes.c_uint32),
                ("global_576ba4", ctypes.c_uint32),
                ("global_576ba8", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-object-table-reset-") as d:
        so = Path(d) / "object-table-reset.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        str(ROOT / "von/i960/recovered_object_table_reset_bd6b8.c"),
                        "-o", str(so)], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_object_table_reset_bd6b8
        fn.argtypes = [ctypes.POINTER(State), ctypes.c_uint32, ctypes.c_uint32]
        state = State()
        ctypes.memset(ctypes.byref(state), 0xa5, ctypes.sizeof(state))
        fn(ctypes.byref(state), 7, 7)
        assert list(state.object_table_200) == [0] * 32
        assert (state.global_576ba0, state.global_576ba4, state.global_576ba8) == (0, 0xa5a5a5a5, 0)
        state.global_576ba0 = 0xa5a5a5a5
        state.global_576ba4 = 0xa5a5a5a5
        state.global_576ba8 = 0xa5a5a5a5
        fn(ctypes.byref(state), 8, 7)
        assert (state.global_576ba0, state.global_576ba4, state.global_576ba8) == (0xa5a5a5a5, 0, 0)
        print("PASS: object table reset and reference-dependent latch clear")


if __name__ == "__main__":
    main()
