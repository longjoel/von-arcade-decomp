#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_table_90c10.c"

class PacketPlan(ctypes.Structure):
    _fields_ = [("remainder_word", ctypes.c_uint32), ("frame_word", ctypes.c_uint32),
                ("frame_readback", ctypes.c_uint32), ("fifo_word", ctypes.c_uint32 * 14),
                ("fifo_count", ctypes.c_uint32)]
class WindowPlan(ctypes.Structure):
    _fields_ = [("table_base", ctypes.c_uint32), ("table_index", ctypes.c_uint32),
                ("table_word", ctypes.c_uint32 * 3), ("control_address", ctypes.c_uint32),
                ("control_value", ctypes.c_uint32), ("publish_address", ctypes.c_uint32),
                ("published", ctypes.c_uint32), ("completion_word", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "geometry_table.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    packet_fn = ctypes.CDLL(str(library)).recovered_geometry_table_packet_90c10
    packet_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                          ctypes.POINTER(PacketPlan)]
    packet = PacketPlan(); packet_fn(7, 0x12345678, 0xdeadbeef, ctypes.byref(packet))
    assert list(packet.fifo_word) == [5, 18, 7, 0x40e00000, 0x41800000,
                                           0x12345678, 21, 0xb800, 19,
                                           0x40400000, 0x40400000, 0x40400000,
                                           58, 0xdeadbeef]
    assert packet.fifo_count == 14
    window_fn = ctypes.CDLL(str(library)).recovered_geometry_table_window_90ccc
    window_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
                          ctypes.POINTER(WindowPlan)]
    words = (ctypes.c_uint32 * 3)(0x11111111, 0x22222222, 0x33333333)
    window = WindowPlan(); window_fn(7, words, ctypes.byref(window))
    assert (window.table_base, window.table_index, list(window.table_word)) == (
        0x2be52b0, 84, [0x11111111, 0x22222222, 0x33333333])
    assert (window.control_address, window.control_value, window.publish_address,
            window.published, window.completion_word) == (0x800010, 0x101,
                                                          0x804000, 1, 6)
    words[0] = 0
    window_fn(7, words, ctypes.byref(window))
    assert window.published == 0
    for name, operand in (("recovered_geometry_table_packet_90d50", 0xc000),
                          ("recovered_geometry_table_packet_90e80", 0xc800)):
        sibling_fn = getattr(ctypes.CDLL(str(library)), name)
        sibling_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                               ctypes.POINTER(PacketPlan)]
        sibling = PacketPlan(); sibling_fn(11, 0xabcdef01, 0x10203040, ctypes.byref(sibling))
        assert list(sibling.fifo_word) == [5, 18, 11, 0x40e00000, 0x41800000,
                                           0xabcdef01, 21, operand, 19,
                                           0x40400000, 0x40400000, 0x40400000,
                                           58, 0x10203040]
        assert sibling.fifo_count == 14
    variant_fn = ctypes.CDLL(str(library)).recovered_geometry_table_packet_variant
    variant_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                           ctypes.c_uint32, ctypes.POINTER(PacketPlan)]
    variant = PacketPlan()
    variant_fn(13, 0xabcdef01, 0xdead, 0x10203040, ctypes.byref(variant))
    assert variant.fifo_word[2] == 13
    assert variant.fifo_word[5] == 0xabcdef01
    assert variant.fifo_word[7] == 0xdead
    assert variant.fifo_word[13] == 0x10203040
    assert variant.fifo_count == 14
print("recovered geometry table 0x90c10 packet: ok")
