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
        "hardware_status_called", "store_count")] + [
            ("store_address_%d" % i, ctypes.c_uint32) for i in range(13)] + [
            ("store_value_%d" % i, ctypes.c_uint32) for i in range(13)] + [
            ("call_count", ctypes.c_uint32)] + [
            ("call_target_%d" % i, ctypes.c_uint32) for i in range(3)]


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
    actual = tuple(getattr(out, name) for name, _ in Init._fields_[:9])
    expected = (1, 0, 1, 0, 0, 0x258, 1, 1, 1)
    if actual != expected:
        raise SystemExit("0x186f0 startup initialization mismatch")
    assert out.store_count == 13
    assert tuple(getattr(out, "store_address_%d" % i) for i in range(13)) == (
        0x5039F8, 0x504C84, 0x5024D4, 0x503A00, 0x5039F4, 0x5039F0,
        0x503AAC, 0x503A7C, 0x5770F0, 0x504C88, 0x503AB4, 0x503AB8,
        0x504D10)
    assert tuple(getattr(out, "store_value_%d" % i) for i in range(13)) == (
        0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0x64, 0x258, 0xFFFFFFFF)
    assert (out.call_count, out.call_target_0, out.call_target_1,
            out.call_target_2) == (3, 0x186C0, 0x18960, 0x18A10)

print("PASS: 0x186f0 startup main-data initialization")
