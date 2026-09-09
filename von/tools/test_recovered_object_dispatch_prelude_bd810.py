#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class State(ctypes.Structure):
    _fields_ = [("object_table", ctypes.c_uint8 * 32),
                ("record_halfword", ctypes.c_uint16 * 32),
                ("global_576ba0", ctypes.c_uint32),
                ("global_576ba4", ctypes.c_uint32),
                ("global_576ba8", ctypes.c_uint32)]


class Result(ctypes.Structure):
    _fields_ = [("accepted_index", ctypes.c_uint32 * 32),
                ("dispatch_target", ctypes.c_uint32 * 32),
                ("context_address", ctypes.c_uint32 * 32),
                ("masked_halfword", ctypes.c_uint16 * 32),
                ("accepted_count", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-object-dispatch-prelude-bd810-") as d:
        so = Path(d) / "object-dispatch-prelude.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        str(ROOT / "von/i960/recovered_object_dispatch_prelude_bd810.c"),
                        "-o", str(so)], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_object_dispatch_prelude_bd810
        fn.argtypes = [ctypes.POINTER(State), ctypes.c_uint32,
                       ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(Result)]
        state = State()
        for index in range(32):
            state.object_table[index] = 0xcd
        state.object_table[0] = 2
        state.record_halfword[0] = 0x123f
        state.global_576ba4 = 0x11111111
        state.global_576ba8 = 0x22222222
        dispatch = (ctypes.c_uint32 * 256)(*[(i * 8) for i in range(256)])
        result = Result()
        fn(ctypes.byref(state), 0, dispatch, ctypes.byref(result))
        assert state.global_576ba0 == 0x22222222
        assert state.global_576ba8 == 0x11111111
        assert result.accepted_count == 1
        assert (result.accepted_index[0], result.dispatch_target[0],
                result.context_address[0], result.masked_halfword[0]) == (0, 16, 0x5658a0, 0x1220)
        state.global_576ba8 = 0x33333333
        fn(ctypes.byref(state), 1, dispatch, ctypes.byref(result))
        assert state.global_576ba0 == 0x33333333
        assert result.accepted_count == 0
        print("PASS: gated alternate object dispatch prelude")


if __name__ == "__main__":
    main()
