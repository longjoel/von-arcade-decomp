#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_table_90c10.c"

class Plan(ctypes.Structure):
    _fields_ = [("source_value", ctypes.c_uint32), ("threshold", ctypes.c_uint32),
                ("adjusted_value", ctypes.c_uint32 * 3), ("call_helper", ctypes.c_uint32 * 3),
                ("completion_word", ctypes.c_uint32),
                ("helper_target", ctypes.c_uint32 * 3),
                ("operand_word", ctypes.c_uint32 * 3)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "geometry_table.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    fn = ctypes.CDLL(str(library)).recovered_geometry_table_dispatch_91624
    fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]
    plan = Plan(); fn(0x109 + 240, ctypes.byref(plan))
    assert plan.threshold == 240
    assert list(plan.adjusted_value) == [240, 230, 220]
    assert list(plan.call_helper) == [1, 1, 1] and plan.completion_word == 6
    assert list(plan.helper_target) == [0x90c10, 0x90d50, 0x90e80]
    assert list(plan.operand_word) == [0xb800, 0xc000, 0xc800]
    fn(0x109 + 239, ctypes.byref(plan))
    assert list(plan.call_helper) == [1, 1, 1]
    fn(0x109 + 241, ctypes.byref(plan))
    assert list(plan.call_helper) == [0, 1, 1]
    paired_fn = ctypes.CDLL(str(library)).recovered_geometry_table_dispatch_91df4
    paired_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]
    paired_fn(0x109 + 240, ctypes.byref(plan))
    assert list(plan.adjusted_value) == [240, 230, 220]
    assert list(plan.call_helper) == [1, 1, 1] and plan.completion_word == 6
print("recovered geometry table 0x91624 dispatcher: ok")
