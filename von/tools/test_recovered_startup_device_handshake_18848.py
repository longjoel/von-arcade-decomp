#!/usr/bin/env python3
"""Validate the startup device/status handshake at i960 0x18848."""
import ctypes
import pathlib
import subprocess
import tempfile


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "startup_flag", "controller_status", "ready_status", "device_word",
        "gate_entered", "mode_before", "phase_before", "mode_after",
        "phase_after", "saved_mode_address", "saved_phase_address",
        "command_address", "command_value", "device_command_address",
        "device_command_value", "completion_seen", "completion_services",
        "retry_target")]


root = pathlib.Path(__file__).parents[2]
with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "startup-handshake.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I",
                    str(root / "von/i960"), "-o", str(so),
                    str(root / "von/i960/recovered_startup_device_handshake_18848.c")],
                   check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_device_handshake_18848
    fn.argtypes = [ctypes.c_uint32] * 6 + [ctypes.POINTER(Result)]
    out = Result()

    fn(0, 0x4, 0, 0x41, 2, 9, ctypes.byref(out))
    assert (out.gate_entered, out.mode_after, out.phase_after,
            out.completion_seen, out.retry_target) == (1, 5, 0, 0, 0x187e4)

    fn(0, 0, 0, 0x50, 5, 0, ctypes.byref(out))
    assert (out.gate_entered, out.completion_seen, out.completion_services,
            out.command_value, out.device_command_value,
            out.retry_target) == (0, 1, 2, 4, 0x0f0f, 0x18724)

    fn(1, 0x4, 1, 0x50, 7, 3, ctypes.byref(out))
    assert (out.gate_entered, out.completion_seen, out.mode_after,
            out.phase_after, out.retry_target) == (0, 0, 7, 3, 0x187e4)

print("PASS: 0x18848 startup device handshake")
