#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_packet_93700.c"

class P11(ctypes.Structure):
    _fields_ = [("input_word", ctypes.c_uint32 * 3), ("tail_word", ctypes.c_uint32),
                ("frame_readback", ctypes.c_uint32), ("fifo_word", ctypes.c_uint32 * 11),
                ("fifo_count", ctypes.c_uint32)]
class P12(ctypes.Structure):
    _fields_ = [("input_word", ctypes.c_uint32 * 3), ("fill_word", ctypes.c_uint32),
                ("tail_word", ctypes.c_uint32), ("frame_readback", ctypes.c_uint32),
                ("fifo_word", ctypes.c_uint32 * 12), ("fifo_count", ctypes.c_uint32)]
class W(ctypes.Structure):
    _fields_ = [("window_word", ctypes.c_uint32 * 4), ("control_address", ctypes.c_uint32),
                ("control_value", ctypes.c_uint32), ("publish_address", ctypes.c_uint32),
                ("completion_word", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "geometry.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    dll = ctypes.CDLL(str(library))
    inputs = (ctypes.c_uint32 * 3)(1, 2, 3)
    f11 = dll.recovered_geometry_packet_93700
    f11.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32, ctypes.c_uint32,
                    ctypes.POINTER(P11)]
    p11 = P11(); f11(inputs, 31 + 27, 0x1234, ctypes.byref(p11))
    assert list(p11.fifo_word) == [5, 18, 1, 2, 3, 19,
                                   0x3dcccccd, 0x3dcccccd, 0x3dcccccd, 58, 0x1234]
    assert p11.fifo_count == 11
    f12 = dll.recovered_geometry_packet_937ec
    f12.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32, ctypes.c_uint32,
                    ctypes.c_uint32, ctypes.POINTER(P12)]
    p12 = P12(); f12(inputs, 0x3dcccccd, 42, 0x5678, ctypes.byref(p12))
    assert list(p12.fifo_word) == [6, 5, 18, 1, 2, 3, 19,
                                   0x3dcccccd, 0x3dcccccd, 0x3dcccccd, 42, 0x5678]
    w = W(); dll.recovered_geometry_window_93700(ctypes.byref(w))
    assert list(w.window_word) == [0x400cec, 0x400d1c, 0x84ce4f, 0]
    assert (w.control_address, w.control_value, w.publish_address, w.completion_word) == \
           (0x800010, 0x101, 0x804000, 6)
print("recovered geometry 0x93700/0x937ec packets: ok")
