#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_calibration_90fc0.c"

class Plan(ctypes.Structure):
    _fields_ = [("source_value", ctypes.c_uint32), ("lower_guard", ctypes.c_uint32),
                ("branch_target", ctypes.c_uint32), ("branch_class", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "calibration.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    fn = ctypes.CDLL(str(library)).recovered_geometry_calibration_90fc0
    fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
    plan = Plan(); fn(0x50, 0x50, ctypes.byref(plan))
    assert (plan.branch_target, plan.branch_class) == (0x9139c, 0)
    for value, target in ((0x8b, 0x91008), (0x8c, 0x9107c),
                          (0xb8, 0x9139c), (0xb9, 0x91124),
                          (0x108, 0x91180), (0x109, 0x911a8),
                          (0x310, 0x912d8), (0x315, 0x9139c),
                          (0x316, 0x91308), (0x379, 0x91308),
                          (0x37a, 0x9139c)):
        fn(value, 0, ctypes.byref(plan))
        assert plan.branch_target == target, (hex(value), hex(plan.branch_target), hex(target))
print("recovered geometry calibration 0x90fc0 branch partition: ok")
