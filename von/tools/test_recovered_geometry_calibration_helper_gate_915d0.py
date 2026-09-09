#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_calibration_90fc0.c"

class Plan(ctypes.Structure):
    _fields_ = [("r15_value", ctypes.c_uint32), ("source_value", ctypes.c_uint32),
                ("remainder", ctypes.c_uint32), ("helper_target", ctypes.c_uint32),
                ("table_base", ctypes.c_uint32), ("flag_value", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "calibration.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    fn = ctypes.CDLL(str(library)).recovered_geometry_calibration_helper_gate_915d0
    fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
    plan = Plan(); fn(1, 4, ctypes.byref(plan))
    assert (plan.remainder, plan.helper_target, plan.table_base, plan.flag_value) == (
        1, 0x8e310, 0x2be2a14, 1)
    fn(1, 5, ctypes.byref(plan))
    assert (plan.remainder, plan.table_base, plan.flag_value) == (2, 0x2be296c, 0)
    fn(0, 4, ctypes.byref(plan))
    assert (plan.table_base, plan.flag_value) == (0x2be296c, 0)
    paired_fn = ctypes.CDLL(str(library)).recovered_geometry_calibration_helper_gate_91d94
    paired_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
    paired_fn(1, 4, ctypes.byref(plan))
    assert (plan.remainder, plan.table_base, plan.flag_value) == (1, 0x2be2a14, 1)
    remi_fn = ctypes.CDLL(str(library)).recovered_geometry_calibration_helper_gate_91dac
    remi_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
    remi_fn(1, 5, ctypes.byref(plan))
    assert (plan.remainder, plan.table_base, plan.flag_value) == (2, 0x2be296c, 0)
print("recovered geometry calibration 0x915d0 helper gate: ok")
