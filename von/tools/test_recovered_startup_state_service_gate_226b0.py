#!/usr/bin/env python3
"""Validate the route partition at i960 0x226b0."""
import ctypes
import pathlib
import subprocess
import tempfile


class Gate(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32 if name != "counter_minus_ten" else ctypes.c_int32)
                for name in ("route", "counter_minus_ten", "sentinel_value",
                             "transfer_source", "transfer_destination",
                             "transfer_width", "transfer_height",
                             "cleared_field_count", "counter_incremented")]


root = pathlib.Path(__file__).parents[2]
with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "gate.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(root / "von/i960/recovered_startup_state_service_gate_226b0.c"),
                    "-o", str(so)], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_state_service_gate_226b0
    fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Gate)]
    for counter, adjusted, route, cleared in (
        (0, -10, 0, 0), (10, 0, 0, 0), (11, 1, 1, 0),
        (12, 2, 2, 2), (13, 3, 3, 0)):
        out = Gate()
        fn(counter, ctypes.byref(out))
        if (out.counter_minus_ten, out.route, out.cleared_field_count,
                out.counter_incremented) != (adjusted, route, cleared, 1):
            raise SystemExit("0x226b0 route mismatch")
        if (out.sentinel_value, out.transfer_source,
                out.transfer_destination, out.transfer_width,
                out.transfer_height) != (0x8000, 0x021FD49D0,
                                          0x01004000, 48, 2):
            raise SystemExit("0x226b0 transfer constants mismatch")

print("PASS: 0x226b0 startup state-service gate")
