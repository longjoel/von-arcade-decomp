#!/usr/bin/env python3
"""Validate the bounded state-update slice at i960 0x3540."""
import ctypes
import pathlib
import subprocess
import tempfile


class Step(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("cleared_status_byte", "bit3_set", "next_state")]


root = pathlib.Path(__file__).parents[2]
with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "step.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(root / "von/i960/recovered_input_state_step_3540.c"),
                    "-o", str(so)], check=True)
    fn = ctypes.CDLL(str(so)).recovered_input_state_step_3540
    fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Step)]
    for state in (0, 1, 14, 15, 16, 0xFFFFFFFF):
        for status, expected in ((0x00, 0), (0x08, state + 1 if state <= 15 else state)):
            result = Step()
            fn(state, status, ctypes.byref(result))
            actual = (result.cleared_status_byte, result.bit3_set,
                      result.next_state)
            wanted = (1, 1 if status & 8 else 0, expected)
            if actual != wanted:
                raise SystemExit("0x3540 state-step mismatch")

print("PASS: 0x3540 input state step")
