#!/usr/bin/env python3
"""Validate the recovered i960 0x37130 frame-step dispatch (0x37350-0x37388).

Compiles von/i960/recovered_framestate_dispatch.c with
    cc -std=c11 -Wall -Wextra -Werror -shared -fPIC
and drives the pure core with a synthetic 43-entry arm table so the gating and
selection are checked without the absolute-address arm bodies.

Covered listing spans:
    0x37350-0x37354   load +0x172, bbs 15 rejects a negative phase
    0x3735c-0x37368   state > 42 skips
    0x37378-0x37380   null 0x37130 entry skips
    0x37388           non-null entry is called with the object
"""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
CORE = ROOT / "von/i960/recovered_framestate_dispatch.c"
RUN = ROOT / "von/i960/recovered_framestate_dispatch_run.c"
ARMS = ROOT / "von/i960/recovered_framestate_arms.c"
ACTION = ROOT / "von/i960/recovered_action_31.c"

CC = ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC"]

OBJ_SIZE = 0x200
ARM_COUNT = 43
ARMED_STATES = (0, 15, 16, 17, 19, 23, 24, 26, 28, 29, 31, 33, 35, 37)

ArmFn = ctypes.CFUNCTYPE(ctypes.c_uint32,
                         ctypes.POINTER(ctypes.c_ubyte))
BytePtr = ctypes.POINTER(ctypes.c_ubyte)


def u16(ptr, offset):
    return ctypes.cast(ctypes.byref(ptr, offset),
                       ctypes.POINTER(ctypes.c_uint16))[0]


def set_u16(ptr, offset, value):
    ctypes.cast(ctypes.byref(ptr, offset),
                ctypes.POINTER(ctypes.c_uint16))[0] = value & 0xffff


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "framestate-dispatch.so"
        subprocess.run(CC + [str(CORE), str(RUN), str(ARMS), str(ACTION),
                             "-o", str(library)], check=True)
        recovered = ctypes.CDLL(str(library))

        core = recovered.recovered_framestate_dispatch_core
        core.argtypes = [BytePtr, ctypes.POINTER(ArmFn), ctypes.c_uint32]
        core.restype = ctypes.c_uint32

        # The run wrapper is loaded to prove the symbol resolves, but it is not
        # called here: its arm bodies read absolute i960 addresses.
        run = recovered.recovered_framestate_dispatch_run
        run.argtypes = [BytePtr]
        run.restype = ctypes.c_uint32

        calls = []
        keepers = []
        table = (ArmFn * ARM_COUNT)()

        for state in ARMED_STATES:
            def body(obj, _state=state):
                calls.append(_state)
                return 1
            arm = ArmFn(body)
            keepers.append(arm)
            table[state] = arm

        obj = (ctypes.c_ubyte * OBJ_SIZE)()
        obj_ptr = ctypes.cast(obj, BytePtr)

        def dispatch(state):
            calls.clear()
            set_u16(obj, 0x172, state)
            return core(obj_ptr, table, ARM_COUNT)

        for state in ARMED_STATES:
            assert dispatch(state) == 1, hex(state)
            assert calls == [state], (hex(state), calls)

        # 0x37378: null table entries (states without a recovered arm) skip.
        for state in (1, 5, 14, 18, 20, 21, 22, 25, 27, 30, 32, 34, 36, 38, 42):
            assert dispatch(state) == 0, hex(state)
            assert calls == [], (hex(state), calls)

        # 0x3735c: the phase gate rejects any state above 42.
        assert dispatch(43) == 0
        assert calls == []

        # 0x37354: the high bit marks a phase that never dispatches.
        assert dispatch(0x8000) == 0
        assert dispatch(0x8000 | 16) == 0
        assert calls == []

    print("PASS: recovered i960 0x37130 frame-step dispatch (0x371e0)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
