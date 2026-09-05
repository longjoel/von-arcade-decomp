#!/usr/bin/env python3
"""Validate the recovered 0x2c70 input flag dispatch table."""
import ctypes
import pathlib
import subprocess
import tempfile


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "flag-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_flag_dispatch_2c70.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    lib.recovered_flag_dispatch_route_count.restype = ctypes.c_uint32
    target_fn = lib.recovered_flag_dispatch_target
    target_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                          ctypes.POINTER(ctypes.c_uint32)]
    target_fn.restype = ctypes.c_uint32

    def route(entry, flag):
        is_bal = ctypes.c_uint32(99)
        target = target_fn(entry, flag, ctypes.byref(is_bal))
        return target, is_bal.value

    assert lib.recovered_flag_dispatch_route_count() == 4
    assert route(0x2C70, 0) == (0x27B8, 1)
    assert route(0x2C70, 7) == (0x2BB0, 0)
    assert route(0x2C90, 0) == (0x2798, 1)
    assert route(0x2C90, 1) == (0x2C10, 0)
    assert route(0x2CB0, 0) == (0x2CD8, 1)
    assert route(0x2CB0, 1) == (0x2CF8, 1)
    assert route(0x2D60, 0) == (0x2D88, 1)
    assert route(0x2D60, 0xFFFFFFFF) == (0x2DA0, 0)
    assert route(0x2C00, 0) == (0, 0)

print("PASS: 0x2c70 flag dispatch table")
