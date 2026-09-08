#!/usr/bin/env python3
"""Validate the deterministic startup prefix at i960 0x186f0."""
import ctypes
import pathlib
import subprocess
import tempfile


class Init(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "stack_counter_seed", "stack_counter_after_drain",
        "startup_state_cleared", "startup_mode_flag",
        "startup_service_counter", "startup_timeout",
        "input_initializer_called", "system_setup_called",
        "hardware_status_called")]


root = pathlib.Path(__file__).parents[2]
with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "init.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(root / "von/i960/recovered_startup_main_data_init_186f0.c"),
                    "-o", str(so)], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_main_data_init_186f0
    fn.argtypes = [ctypes.POINTER(Init)]
    out = Init()
    fn(ctypes.byref(out))
    actual = tuple(getattr(out, name) for name, _ in Init._fields_)
    expected = (1, 0, 1, 0, 0, 0x258, 1, 1, 1)
    if actual != expected:
        raise SystemExit("0x186f0 startup initialization mismatch")

print("PASS: 0x186f0 startup main-data initialization")
