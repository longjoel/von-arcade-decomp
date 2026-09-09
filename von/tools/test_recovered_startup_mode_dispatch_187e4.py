#!/usr/bin/env python3
"""Validate the startup mode-table selector at i960 0x18800."""
import ctypes
import pathlib
import subprocess
import tempfile


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "table_address", "mode_address", "phase_address", "mode_before",
        "mode_index", "selected_target", "callx_performed",
        "null_target_repaired", "mode_after", "phase_after",
        "continuation")]


root = pathlib.Path(__file__).parents[2]
with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "startup-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I",
                    str(root / "von/i960"), "-o", str(so),
                    str(root / "von/i960/recovered_startup_mode_dispatch_187e4.c")],
                   check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode_dispatch_187e4
    fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
                   ctypes.POINTER(Result)]

    handlers = (ctypes.c_uint32 * 16)()
    handlers[0] = 0x3c40
    out = Result()
    fn(0x20, handlers, ctypes.byref(out))
    assert (out.mode_index, out.selected_target, out.callx_performed,
            out.null_target_repaired, out.mode_after, out.phase_after,
            out.continuation) == (0, 0x3c40, 1, 0, 0x20, 0, 0x18848)

    handlers[9] = 0
    fn(9, handlers, ctypes.byref(out))
    assert (out.mode_index, out.selected_target, out.callx_performed,
            out.null_target_repaired, out.mode_after, out.phase_after) == \
        (9, 0, 0, 1, 1, 0)

print("PASS: 0x187e4 startup mode dispatch selector")
