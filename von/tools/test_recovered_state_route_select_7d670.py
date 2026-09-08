#!/usr/bin/env python3
"""Check the seven-entry selector scan at i960 0x7d670."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_route_select_7d670.c"


class Record(ctypes.Structure):
    _fields_ = [("first", ctypes.c_int16),
                ("metric", ctypes.c_int16),
                ("enabled", ctypes.c_int16)]


class Selection(ctypes.Structure):
    _fields_ = [("selected_index", ctypes.c_uint32),
                ("selected_metric", ctypes.c_int16),
                ("fallback_status", ctypes.c_uint32),
                ("packet_target", ctypes.c_uint32),
                ("record_table_base", ctypes.c_uint32),
                ("record_stride", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-route-select.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_route_select_7d670
    function.argtypes = [Record * 7, ctypes.c_int32]
    function.restype = Selection

    records = (Record * 7)(*(Record(0, 0, 0) for _ in range(7)))
    assert (function(records, 4).selected_index,
            function(records, 4).fallback_status,
            function(records, 4).packet_target) == (0xffffffff, 11, 0)
    assert function(records, 5).fallback_status == 10

    records[1] = Record(12, 20, 1)
    records[3] = Record(14, -3, 1)
    records[5] = Record(16, 9, 1)
    result = function(records, 0)
    assert (result.selected_index, result.selected_metric,
            result.fallback_status, result.packet_target) == (3, -3, 0, 0x7D7F4)
    assert (result.record_table_base, result.record_stride) == (0x505060, 6)

    records[6] = Record(18, -3, 1)
    assert function(records, 0).selected_index == 3

print("recovered 0x7d670 selector-scan vectors: ok")
