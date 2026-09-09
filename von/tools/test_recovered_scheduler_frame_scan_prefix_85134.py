#!/usr/bin/env python3
"""Check the frame-scan setup and early gate at i960 0x85134."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_frame_scan_prefix_85134.c"


class Plan(ctypes.Structure):
    _fields_ = [("frame_record_address", ctypes.c_uint32),
                ("table_base", ctypes.c_uint32),
                ("table_field_address", ctypes.c_uint32),
                ("frame_upper_g8", ctypes.c_uint32),
                ("frame_upper_g9", ctypes.c_uint32),
                ("frame_target_g8", ctypes.c_uint32),
                ("frame_target_g9", ctypes.c_uint32),
                ("field_86", ctypes.c_uint32),
                ("exits_to_853a0", ctypes.c_uint32),
                ("continues_to_851a8", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib85134.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_frame_scan_prefix_85134
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    result = function(3, 2, 0xffff5678, 0x9abcdef0, 49)
    assert (result.frame_record_address, result.table_base,
            result.table_field_address) == (0x5096d0, 0x507d20, 0x507da6)
    assert (result.frame_upper_g8, result.frame_upper_g9,
            result.frame_target_g8, result.frame_target_g9) == (0xffff, 0x9abc,
                                                                 0xffb9, 0x9a76)
    assert (result.field_86, result.exits_to_853a0,
            result.continues_to_851a8) == (49, 1, 0)
    result = function(0, 0, 0xffff0000, 0, 0x10032)
    assert (result.field_86, result.exits_to_853a0,
            result.continues_to_851a8) == (50, 0, 1)
    result = function(0, 0, 0, 0, 0x10032)
    assert (result.field_86, result.exits_to_853a0,
            result.continues_to_851a8) == (0, 1, 0)

print("recovered 0x85134 frame-scan-prefix vectors: ok")
