#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_calibration_90fc0.c"

class Plan(ctypes.Structure):
    _fields_ = [("computed_word", ctypes.c_uint32), ("address_word_0", ctypes.c_uint32),
                ("address_word_1", ctypes.c_uint32), ("xor_word_0", ctypes.c_uint32),
                ("xor_word_1", ctypes.c_uint32), ("auxiliary_word", ctypes.c_uint32),
                ("fifo_word", ctypes.c_uint32 * 16), ("fifo_count", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "calibration.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    fn = ctypes.CDLL(str(library)).recovered_geometry_calibration_packet_91ccc
    fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                   ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                   ctypes.POINTER(Plan)]
    plan = Plan(); fn(1, 2, 3, 4, 5, 6, ctypes.byref(plan))
    assert list(plan.fifo_word) == [6, 5, 18, 1, 2, 3, 21, 0x4000, 47,
                                   4, 5, 6, 19, 0x3e4ccccd,
                                   0x3e4ccccd, 0x3e4ccccd]
    assert plan.fifo_count == 16
print("recovered geometry calibration 0x91ccc packet: ok")
