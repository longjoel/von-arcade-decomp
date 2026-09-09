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
    with tempfile.TemporaryDirectory(prefix="von-object-dispatch-prelude-") as d:
        so = Path(d) / "object-dispatch-prelude.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        str(ROOT / "von/i960/recovered_object_dispatch_prelude_bd730.c"),
                        "-o", str(so)], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_object_dispatch_prelude_bd730
        fn.argtypes = [ctypes.POINTER(State), ctypes.POINTER(ctypes.c_uint32),
                       ctypes.POINTER(Result)]
        state = State()
        for index in range(32):
            state.object_table[index] = 0xcd
        state.object_table[0] = 1
        state.object_table[1] = 0xcc
        state.object_table[2] = 0xcd
        state.record_halfword[0] = 0x1237
        state.record_halfword[1] = 0xabff
        state.global_576ba4 = 0x11111111
        state.global_576ba8 = 0x22222222
        dispatch = (ctypes.c_uint32 * 256)(*[(i * 4) for i in range(256)])
        result = Result()
        fn(ctypes.byref(state), dispatch, ctypes.byref(result))
        assert state.global_576ba4 == state.global_576ba8 == 0x22222222
        assert result.accepted_count == 2
        assert list(result.accepted_index[:2]) == [0, 1]
        assert list(result.dispatch_target[:2]) == [4, 0xcc * 4]
        assert list(result.context_address[:2]) == [0x565320, 0x56534c]
        assert list(result.masked_halfword[:2]) == [0x1220, 0xabe0]
        assert (state.record_halfword[0], state.record_halfword[1]) == (0x1220, 0xabe0)
        print("PASS: object dispatch prelude gate, lookup, and mask")


if __name__ == "__main__":
    main()
