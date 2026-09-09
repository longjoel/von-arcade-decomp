#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_calibration_90fc0.c"

class Plan(ctypes.Structure):
    _fields_ = [("record_word", ctypes.c_uint32),
                ("computed_word", ctypes.c_uint32 * 2),
                ("auxiliary_word", ctypes.c_uint32),
                ("frame_readback", ctypes.c_uint32),
                ("fifo_word", ctypes.c_uint32 * 10),
                ("fifo_count", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "calibration.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    fn = ctypes.CDLL(str(library)).recovered_geometry_calibration_packet_92070
    fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                   ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
    plan = Plan(); fn(0x11, 0x22, 0x33, 0x44, 0x55, ctypes.byref(plan))
    assert list(plan.fifo_word) == [6, 5, 18, 0x11, 0x22, 0x33,
                                    21, 0xc000, 0x44, 0x55]
    assert plan.fifo_count == 10
print("recovered geometry calibration 0x92070 packet: ok")
