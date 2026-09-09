#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_calibration_90fc0.c"

class Plan(ctypes.Structure):
    _fields_ = [("input_word", ctypes.c_uint32 * 3), ("fifo_word", ctypes.c_uint32 * 7),
                ("fifo_count", ctypes.c_uint32), ("operand_word", ctypes.c_uint32),
                ("helper_target", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "calibration.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    fn = ctypes.CDLL(str(library)).recovered_geometry_calibration_packet_91fac
    fn.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(Plan)]
    inputs = (ctypes.c_uint32 * 3)(10, 20, 30)
    plan = Plan(); fn(inputs, ctypes.byref(plan))
    assert list(plan.fifo_word) == [5, 18, 10, 20, 30, 21, 0xc000]
    assert (plan.fifo_count, plan.operand_word, plan.helper_target) == (7, 0xc000, 0x8e310)
print("recovered geometry calibration 0x91fac packet: ok")
