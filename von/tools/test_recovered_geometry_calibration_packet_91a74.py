#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_calibration_90fc0.c"

class PacketPlan(ctypes.Structure):
    _fields_ = [("input_word", ctypes.c_uint32 * 3), ("fifo_word", ctypes.c_uint32 * 9),
                ("fifo_count", ctypes.c_uint32), ("frame_readback", ctypes.c_uint32)]
class WindowPlan(ctypes.Structure):
    _fields_ = [("window_word", ctypes.c_uint32 * 4), ("control_address", ctypes.c_uint32),
                ("control_value", ctypes.c_uint32), ("publish_address", ctypes.c_uint32),
                ("completion_word", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "calibration.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    packet_fn = ctypes.CDLL(str(library)).recovered_geometry_calibration_packet_91a74
    packet_fn.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32,
                          ctypes.POINTER(PacketPlan)]
    inputs = (ctypes.c_uint32 * 3)(10, 20, 30)
    packet = PacketPlan(); packet_fn(inputs, 0xdeadbeef, ctypes.byref(packet))
    assert list(packet.fifo_word) == [5, 18, 10, 20, 30, 21, 0xc000, 58, 0xdeadbeef]
    assert packet.fifo_count == 9
    caller_fn = ctypes.CDLL(str(library)).recovered_geometry_calibration_callsite_969c4
    caller_fn.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32,
                          ctypes.POINTER(PacketPlan)]
    calibration = (ctypes.c_uint32 * 3)(1, 2, 3)
    caller = PacketPlan(); caller_fn(calibration, 0x12345678, ctypes.byref(caller))
    assert list(caller.input_word) == [0x41b00000, 0x41ef3333, 0xc141999a]
    assert list(caller.fifo_word) == [5, 18, 0x41b00001, 0x41ef3335,
                                      0xc141999d, 21, 0xc000, 58, 0x12345678]
    window_fn = ctypes.CDLL(str(library)).recovered_geometry_calibration_window_91b10
    window_fn.argtypes = [ctypes.POINTER(WindowPlan)]
    window = WindowPlan(); window_fn(ctypes.byref(window))
    assert list(window.window_word) == [0x403a90, 0x403b18, 0x850387, 0]
    assert (window.control_address, window.control_value, window.publish_address,
            window.completion_word) == (0x800010, 0x101, 0x804000, 6)
print("recovered geometry calibration 0x91a74 packet: ok")
