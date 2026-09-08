#!/usr/bin/env python3
"""Validate explicit state routes recovered from i960 0x25040."""
import ctypes
import pathlib
import subprocess
import tempfile


class Dispatch(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "route", "record_status_copied", "record_work_copied",
        "record_halfword_copied", "state6_record_cleared",
        "state6_association_cleared", "state6_work_cleared",
        "common_tail_present")]


root = pathlib.Path(__file__).parents[2]
with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(root / "von/i960/recovered_state_dispatch_25040.c"),
                    "-o", str(so)], check=True)
    fn = ctypes.CDLL(str(so)).recovered_state_dispatch_25040
    fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Dispatch)]
    for counter, state, route in (
        (12, 0, 1), (12, 1, 1), (12, 2, 0),
        (20, 0, 2), (20, 1, 3), (20, 2, 0),
        (7, 1, 4), (7, 5, 5), (7, 6, 6), (7, 9, 7)):
        out = Dispatch()
        fn(counter, state, ctypes.byref(out))
        if out.route != route or (out.record_status_copied,
                                  out.record_work_copied,
                                  out.record_halfword_copied,
                                  out.common_tail_present) != (1, 1, 1, 1):
            raise SystemExit("0x25040 state route mismatch")
        expected_reset = (1, 1, 1) if route == 6 else (0, 0, 0)
        if (out.state6_record_cleared, out.state6_association_cleared,
                out.state6_work_cleared) != expected_reset:
            raise SystemExit("0x25040 state-6 reset mismatch")

print("PASS: 0x25040 state dispatch plan")
