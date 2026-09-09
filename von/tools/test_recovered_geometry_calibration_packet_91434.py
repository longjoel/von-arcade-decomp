#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_calibration_90fc0.c"

class PacketPlan(ctypes.Structure):
    _fields_ = [("computed_word", ctypes.c_uint32), ("address_word_0", ctypes.c_uint32),
                ("address_word_1", ctypes.c_uint32), ("secondary_word", ctypes.c_uint32),
                ("frame_readback", ctypes.c_uint32), ("fifo_word", ctypes.c_uint32 * 9),
                ("fifo_count", ctypes.c_uint32)]
class WindowPlan(ctypes.Structure):
    _fields_ = [("window_word", ctypes.c_uint32 * 4), ("control_address", ctypes.c_uint32),
                ("control_value", ctypes.c_uint32), ("publish_address", ctypes.c_uint32),
                ("completion_word", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "calibration.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    packet_fn = ctypes.CDLL(str(library)).recovered_geometry_calibration_packet_91434
    packet_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                          ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(PacketPlan)]
    packet = PacketPlan(); packet_fn(1, 2, 3, 4, 0xdeadbeef, ctypes.byref(packet))
    assert list(packet.fifo_word) == [5, 18, 1, 2, 3, 21, 4, 58, 0xdeadbeef]
    assert packet.fifo_count == 9 and packet.secondary_word == 4
    window_fn = ctypes.CDLL(str(library)).recovered_geometry_calibration_window_914d8
    window_fn.argtypes = [ctypes.POINTER(WindowPlan)]
    window = WindowPlan(); window_fn(ctypes.byref(window))
    assert list(window.window_word) == [0x403968, 0x4039f0, 0x850225, 0]
    assert (window.control_address, window.control_value, window.publish_address,
            window.completion_word) == (0x800010, 0x101, 0x804000, 6)
print("recovered geometry calibration 0x91434 packet: ok")
