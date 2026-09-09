#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_calibration_90fc0.c"

class Plan(ctypes.Structure):
    _fields_ = [("input_word", ctypes.c_uint32 * 3), ("secondary_word", ctypes.c_uint32),
                ("fifo_word", ctypes.c_uint32 * 7), ("fifo_count", ctypes.c_uint32),
                ("helper_target", ctypes.c_uint32), ("completion_word", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "calibration.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    fn = ctypes.CDLL(str(library)).recovered_geometry_calibration_packet_91b58
    fn.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32,
                   ctypes.POINTER(Plan)]
    inputs = (ctypes.c_uint32 * 3)(10, 20, 30)
    plan = Plan(); fn(inputs, 40, ctypes.byref(plan))
    assert list(plan.fifo_word) == [5, 18, 10, 20, 30, 21, 40]
    assert (plan.fifo_count, plan.helper_target, plan.completion_word) == (7, 0x8e310, 6)
    for name in ("recovered_geometry_calibration_packet_91bc8",
                 "recovered_geometry_calibration_packet_91c58"):
        sibling_fn = getattr(ctypes.CDLL(str(library)), name)
        sibling_fn.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32,
                               ctypes.POINTER(Plan)]
        sibling = Plan(); sibling_fn(inputs, 40, ctypes.byref(sibling))
        assert list(sibling.fifo_word) == [5, 18, 10, 20, 30, 21, 40]
        assert (sibling.fifo_count, sibling.helper_target, sibling.completion_word) == (
            7, 0x8e310, 6)
print("recovered geometry calibration 0x91b58 packet: ok")
