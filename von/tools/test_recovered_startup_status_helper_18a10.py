#!/usr/bin/env python3
"""Validate the startup status helper at i960 0x18a10."""
import ctypes
import pathlib
import subprocess
import tempfile


class Status(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "mode_byte", "state_flag", "status_service_result",
        "service_gate_open", "state_service_calls", "status_address",
        "state_address", "flag_address", "status_service_call",
        "state_service_call", "loop_first_index", "loop_last_index")]


root = pathlib.Path(__file__).parents[2]
with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "status.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(root / "von/i960/recovered_startup_status_helper_18a10.c"),
                    "-o", str(so)], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_status_helper_18a10
    fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                   ctypes.POINTER(Status)]
    for hardware, expected_mode, expected_flag in (
        (0xFF, 2, 1), (0x101, 1, 0), (0, 3, 0), (0x1234, 3, 0)):
        for startup_mode, expected_calls in ((4, 120), (5, 0)):
            for result in (0, 1):
                out = Status()
                fn(hardware, result, startup_mode, ctypes.byref(out))
                actual = (out.mode_byte, out.state_flag,
                          out.status_service_result, out.service_gate_open,
                          out.state_service_calls)
                open_gate = result == 0 and startup_mode != 5
                wanted = (expected_mode, expected_flag, result,
                          1 if open_gate else 0,
                          expected_calls if result == 0 else 0)
                if actual != wanted:
                    raise SystemExit("0x18a10 status helper mismatch")
                assert (out.status_address, out.state_address, out.flag_address,
                        out.status_service_call, out.state_service_call,
                        out.loop_first_index, out.loop_last_index) == (
                            0x1D00028, 0x5770B1, 0x503A08, 0xC5870,
                            0x18AB0, 0, 0x77)

print("PASS: 0x18a10 startup status helper")
