#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_asset_dispatch_95a00.c"

class Plan(ctypes.Structure):
    _fields_ = [("record_type", ctypes.c_uint32), ("record_flag", ctypes.c_uint32),
                ("mode_address", ctypes.c_uint32), ("mode_value", ctypes.c_uint32),
                ("helper_target", ctypes.c_uint32), ("call_count", ctypes.c_uint32),
                ("selector", ctypes.c_uint32 * 4),
                ("index_word", ctypes.c_uint32 * 4)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "asset-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_geometry_asset_dispatch_95a00
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
    plan = Plan(); function(5, 1, ctypes.byref(plan))
    assert (plan.mode_address, plan.mode_value, plan.helper_target, plan.call_count) == \
           (0x577590, 15, 0xe2120, 4)
    assert list(plan.selector) == [1, 3, 5, 7]
    assert list(plan.index_word) == [20, 21, 22, 23]
    function(7, 0, ctypes.byref(plan))
    assert (plan.mode_value, list(plan.index_word)) == (18, [28, 29, 28, 29])
    function(7, 1, ctypes.byref(plan))
    assert list(plan.index_word) == [28, 29, 30, 31]
print("recovered geometry 0x95a00 asset dispatch: ok")
