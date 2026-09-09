#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_calibration_90fc0.c"

class Plan(ctypes.Structure):
    _fields_ = [("source_value", ctypes.c_uint32), ("branch_target", ctypes.c_uint32),
                ("branch_class", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "calibration.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    fn = ctypes.CDLL(str(library)).recovered_geometry_calibration_secondary_partition_91e60
    fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]
    plan = Plan()
    for value, target in ((0x000, 0x91ea8), (0x12a, 0x91ea8), (0x12b, 0x91ea8),
                          (0x12c, 0x91f30), (0x148, 0x91f30), (0x149, 0x91f30),
                          (0x14a, 0x91edc), (0x274, 0x91edc), (0x275, 0x91edc),
                          (0x276, 0x91f30), (0x292, 0x91f30), (0x293, 0x91f30),
                          (0x294, 0x91f44), (0xffffffff, 0x91f44)):
        fn(value, ctypes.byref(plan))
        assert plan.branch_target == target, (hex(value), hex(plan.branch_target))
print("recovered geometry calibration 0x91e60 partition: ok")
