#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_calibration_90fc0.c"

class Plan(ctypes.Structure):
    _fields_ = [("r10_value", ctypes.c_uint32), ("source_value", ctypes.c_uint32),
                ("remainder", ctypes.c_uint32), ("helper_target", ctypes.c_uint32),
                ("table_base", ctypes.c_uint32), ("flag_address", ctypes.c_uint32),
                ("flag_value", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "calibration.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    fn = ctypes.CDLL(str(library)).recovered_geometry_calibration_helper_gate_921f8
    fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
    plan = Plan(); fn(1, 10, ctypes.byref(plan))
    assert (plan.remainder, plan.table_base, plan.flag_address, plan.flag_value) == \
           (1, 0x2be2a14, 0x5624d8, 1)
    fn(1, 11, ctypes.byref(plan))
    assert (plan.remainder, plan.table_base, plan.flag_value) == (2, 0x2be296c, 0)
    fn(0, 10, ctypes.byref(plan))
    assert (plan.table_base, plan.flag_value) == (0x2be296c, 0)
print("recovered geometry calibration 0x921f8 gate: ok")
