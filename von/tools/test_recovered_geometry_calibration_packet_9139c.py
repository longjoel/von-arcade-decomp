#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_calibration_90fc0.c"

class Plan(ctypes.Structure):
    _fields_ = [("input_word", ctypes.c_uint32 * 3),
                ("calibration_word", ctypes.c_uint32 * 3),
                ("fifo_word", ctypes.c_uint32 * 7), ("fifo_count", ctypes.c_uint32),
                ("helper_target", ctypes.c_uint32), ("operand_word", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "calibration.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    fn = ctypes.CDLL(str(library)).recovered_geometry_calibration_packet_9139c
    fn.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
                   ctypes.POINTER(Plan)]
    inputs = (ctypes.c_uint32 * 3)(10, 20, 30)
    calibration = (ctypes.c_uint32 * 3)(1, 2, 3)
    plan = Plan(); fn(inputs, calibration, ctypes.byref(plan))
    assert list(plan.fifo_word) == [5, 18, 11, 22, 33, 21, 0xc000]
    assert (plan.fifo_count, plan.helper_target, plan.operand_word) == (7, 0x8e310, 0xc000)
    caller_fn = ctypes.CDLL(str(library)).recovered_geometry_calibration_callsite_96964
    caller_fn.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(Plan)]
    caller = Plan(); caller_fn(calibration, ctypes.byref(caller))
    assert list(caller.input_word) == [0x41e00000, 0x41d66666, 0xc17b3333]
    assert list(caller.fifo_word) == [5, 18, 0x41e00001, 0x41d66668,
                                      0xc17b3336, 21, 0xc000]
print("recovered geometry calibration 0x9139c packet: ok")
