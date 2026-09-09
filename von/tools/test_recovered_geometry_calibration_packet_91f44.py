#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_calibration_90fc0.c"

class Plan(ctypes.Structure):
    _fields_ = [("input_word", ctypes.c_uint32), ("masked_word", ctypes.c_uint32),
                ("frame_readback", ctypes.c_uint32), ("fifo_word", ctypes.c_uint32 * 5),
                ("fifo_count", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "calibration.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    fn = ctypes.CDLL(str(library)).recovered_geometry_calibration_packet_91f44
    fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
    plan = Plan(); fn(0x1234, 0xdeadbeef, ctypes.byref(plan))
    assert (plan.masked_word, list(plan.fifo_word), plan.fifo_count) == (
        0x9234, [5, 21, 0x9234, 58, 0xdeadbeef], 5)
print("recovered geometry calibration 0x91f44 packet: ok")
