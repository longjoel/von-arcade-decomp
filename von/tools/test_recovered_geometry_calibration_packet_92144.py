#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_calibration_90fc0.c"

class Plan(ctypes.Structure):
    _fields_ = [("leading_word", ctypes.c_uint32 * 3),
                ("xor_source", ctypes.c_uint32 * 2),
                ("xor_mask", ctypes.c_uint32),
                ("auxiliary_word", ctypes.c_uint32),
                ("fifo_word", ctypes.c_uint32 * 16),
                ("fifo_count", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "calibration.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    fn = ctypes.CDLL(str(library)).recovered_geometry_calibration_packet_92144
    fn.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
                   ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
    leading = (ctypes.c_uint32 * 3)(1, 2, 3)
    payload = (ctypes.c_uint32 * 2)(0x12345678, 0xabcdef01)
    plan = Plan(); fn(leading, payload, 0x4000, 0x99, ctypes.byref(plan))
    assert list(plan.fifo_word) == [6, 5, 18, 1, 2, 3, 21, 0x4000, 47,
                                    0x12341678, 0x99, 0xabcdaf01, 19,
                                    0x3e4ccccd, 0x3e4ccccd, 0x3e4ccccd]
    assert plan.fifo_count == 16
print("recovered geometry calibration 0x92144 packet: ok")
