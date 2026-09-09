#!/usr/bin/env python3
"""Validate the shared 0x1cac8 UI-state helper store schedule."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
MEMORY_SOURCE = ROOT / "von/i960/recovered_memory.c"
HOST_CONTROL_SOURCE = ROOT / "von/i960/recovered_host_control.c"

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "ui-state-helper.so"
    subprocess.run([
        "cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
        str(ROOT / "von/i960/recovered_text.c"), str(MEMORY_SOURCE),
        str(HOST_CONTROL_SOURCE), "-o", str(library)
    ], check=True)
    function = ctypes.CDLL(str(library)).recovered_text_ui_state_helper_plan
    function.argtypes = [
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        *([ctypes.POINTER(ctypes.c_uint32)] * 7),
    ]
    function.restype = ctypes.c_uint32

    values = [ctypes.c_uint32() for _ in range(7)]
    assert function(
        0x12345678, 0x9abcdef0, 0x1cba10, *(ctypes.byref(v) for v in values)
    ) == 1
    assert [v.value for v in values] == [
        0x504cdc, 0x12345678,
        0x504ce0, 0x12345678,
        0x504ce4, 0x9abcdef0,
        0x1cba10,
    ]

print("PASS: 0x1cac8 UI-state helper store schedule")
