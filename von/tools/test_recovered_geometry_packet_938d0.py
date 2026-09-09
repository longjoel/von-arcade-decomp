#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_packet_93700.c"

class Packet(ctypes.Structure):
    _fields_ = [("computed_word", ctypes.c_uint32 * 2),
                ("input_word", ctypes.c_uint32), ("masked_word", ctypes.c_uint32),
                ("context_word", ctypes.c_uint32), ("tail_word", ctypes.c_uint32),
                ("frame_readback", ctypes.c_uint32),
                ("fifo_word", ctypes.c_uint32 * 11), ("fifo_count", ctypes.c_uint32)]
class Packet12(ctypes.Structure):
    _fields_ = [("computed_word", ctypes.c_uint32 * 3),
                ("context_word", ctypes.c_uint32), ("frame_readback", ctypes.c_uint32),
                ("fifo_word", ctypes.c_uint32 * 12), ("fifo_count", ctypes.c_uint32)]
class Window(ctypes.Structure):
    _fields_ = [("window_word", ctypes.c_uint32 * 4), ("control_address", ctypes.c_uint32),
                ("control_value", ctypes.c_uint32), ("publish_address", ctypes.c_uint32),
                ("completion_word", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "geometry.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    dll = ctypes.CDLL(str(library))
    fn = dll.recovered_geometry_packet_938d0
    fn.argtypes = [ctypes.c_uint32] * 7 + [ctypes.POINTER(Packet)]
    p = Packet(); fn(0x11, 0x22, 0x33, 0x4000, 0x44, 58, 0x66, ctypes.byref(p))
    assert list(p.fifo_word) == [6, 5, 44, 0x11, 0x22, 0x33, 0x4000,
                                  0x4000, 0x44, 58, 0x66]
    assert p.fifo_count == 11
    fn12 = dll.recovered_geometry_packet_93a1c
    fn12.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32,
                     ctypes.c_uint32, ctypes.POINTER(Packet12)]
    computed = (ctypes.c_uint32 * 3)(1, 2, 3)
    p12 = Packet12(); fn12(computed, 4, 5, ctypes.byref(p12))
    assert list(p12.fifo_word) == [6, 5, 44, 1, 2, 3, 3, 0x6080, 0x3c80,
                                   4, 58, 5]
    wf = dll.recovered_geometry_window_93964
    wf.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Window)]
    w = Window(); wf(1, 0x77, ctypes.byref(w))
    assert list(w.window_word) == [0xcb094, 0xcb120, 0xa1cc84, 0]
    wf(0, 0x77, ctypes.byref(w))
    assert list(w.window_word) == [0xcb094, 0x59598e, 0xa1cc84, 0x77]
    f5 = dll.recovered_geometry_packet_93dec
    class P5(ctypes.Structure):
        _fields_ = [("input_word", ctypes.c_uint32), ("masked_word", ctypes.c_uint32),
                    ("tail_word", ctypes.c_uint32), ("frame_readback", ctypes.c_uint32),
                    ("fifo_word", ctypes.c_uint32 * 5), ("fifo_count", ctypes.c_uint32)]
    f5.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(P5)]
    p5 = P5(); f5(1, 58, 2, ctypes.byref(p5))
    assert list(p5.fifo_word) == [5, 21, 0x8000, 58, 2]
    class P7(ctypes.Structure):
        _fields_ = [("input_word", ctypes.c_uint32 * 3), ("fifo_word", ctypes.c_uint32 * 7),
                    ("fifo_count", ctypes.c_uint32), ("helper_target", ctypes.c_uint32),
                    ("helper_base", ctypes.c_uint32 * 2), ("helper_offset", ctypes.c_uint32 * 2),
                    ("helper_third", ctypes.c_uint32)]
    f7 = dll.recovered_geometry_packet_93e54
    f7.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
                   ctypes.c_uint32, ctypes.POINTER(P7)]
    words = (ctypes.c_uint32 * 3)(10, 20, 30)
    adds = (ctypes.c_uint32 * 3)(1, 2, 3)
    p7 = P7(); f7(words, adds, 31, ctypes.byref(p7))
    assert list(p7.fifo_word) == [5, 18, 11, 22, 33, 21, 0xc000]
    assert (p7.helper_target, list(p7.helper_base), list(p7.helper_offset), p7.helper_third) == \
           (0x8e310, [0x2b4613a, 0x2b4613a], [0x9cb7a, 0x9cbf2], 31)
    f7_service = dll.recovered_geometry_packet_94d90
    f7_service.argtypes = f7.argtypes
    p7_service = P7(); f7_service(words, adds, 31, ctypes.byref(p7_service))
    assert list(p7_service.fifo_word) == list(p7.fifo_word)
    assert (list(p7_service.helper_offset), p7_service.helper_third) == \
           ([0x9cb7a, 0x9cbf2], 31)
    caller_99198 = dll.recovered_geometry_packet_callsite_99198
    caller_99198.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32,
                             ctypes.POINTER(P7)]
    p7_caller = P7(); caller_99198(adds, 31, ctypes.byref(p7_caller))
    assert list(p7_caller.input_word) == [0x41766666, 0x41bf3333, 0xc0fccccd]
    assert list(p7_caller.fifo_word) == [5, 18, 0x41766667, 0x41bf3335,
                                         0xc0fcccd0, 21, 0xc000]
    class P10(ctypes.Structure):
        _fields_ = [("input_word", ctypes.c_uint32 * 3),
                    ("tail_word", ctypes.c_uint32),
                    ("frame_readback", ctypes.c_uint32),
                    ("fifo_word", ctypes.c_uint32 * 10),
                    ("fifo_count", ctypes.c_uint32)]
    f10 = dll.recovered_geometry_packet_93edc
    f10.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32, ctypes.c_uint32,
                    ctypes.POINTER(P10)]
    p10 = P10(); f10(words, 40, 6, ctypes.byref(p10))
    assert list(p10.fifo_word) == [6, 5, 18, 10, 20, 30, 21, 0xc000, 40, 6]
    class W2(ctypes.Structure):
        _fields_ = [("window_word", ctypes.c_uint32 * 4),
                    ("control_address", ctypes.c_uint32), ("control_value", ctypes.c_uint32),
                    ("publish_address", ctypes.c_uint32), ("completion_word", ctypes.c_uint32)]
    w2 = W2(); dll.recovered_geometry_window_93f8c(ctypes.byref(w2))
    assert list(w2.window_word) == [0x403968, 0x4039f0, 0x850225, 0]
    assert (w2.control_address, w2.control_value, w2.publish_address, w2.completion_word) == \
           (0x800010, 0x101, 0x804000, 6)
    class P16(ctypes.Structure):
        _fields_ = [("computed_word", ctypes.c_uint32 * 2), ("mask_word", ctypes.c_uint32),
                    ("xor_source", ctypes.c_uint32 * 2), ("auxiliary_word", ctypes.c_uint32),
                    ("fifo_word", ctypes.c_uint32 * 16), ("fifo_count", ctypes.c_uint32)]
    f16 = dll.recovered_geometry_packet_93fe4
    f16.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                    ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32, ctypes.POINTER(P16)]
    xor_source = (ctypes.c_uint32 * 2)(0x12345678, 0xabcdef01)
    p16 = P16(); f16(1, 2, 0x4000, xor_source, 9, ctypes.byref(p16))
    assert list(p16.fifo_word) == [6, 5, 18, 1, 44, 2, 21, 0x4000, 47,
                                   0x12341678, 9, 0xabcdaf01, 19,
                                   0x3e4ccccd, 0x3e4ccccd, 0x3e4ccccd]
    class Gate(ctypes.Structure):
        _fields_ = [("r9_value", ctypes.c_uint32), ("divisor_word", ctypes.c_uint32),
                    ("remainder", ctypes.c_uint32), ("active_argument", ctypes.c_uint32),
                    ("helper_target", ctypes.c_uint32), ("table_base", ctypes.c_uint32),
                    ("flag_address", ctypes.c_uint32), ("flag_value", ctypes.c_uint32)]
    gf = dll.recovered_geometry_helper_gate_94080
    gf.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Gate)]
    gate = Gate(); gf(1, 10, 0x77, 0x88, ctypes.byref(gate))
    assert (gate.remainder, gate.active_argument, gate.table_base,
            gate.flag_address, gate.flag_value) == (1, 0x77, 0x2be2a14, 0x5624e0, 1)
    gf(1, 11, 0x77, 0x88, ctypes.byref(gate))
    assert (gate.remainder, gate.active_argument, gate.table_base, gate.flag_value) == \
           (2, 0x88, 0x2be296c, 0)
    f5b = dll.recovered_geometry_packet_94bf0
    class P5B(ctypes.Structure):
        _fields_ = [("frame_readback", ctypes.c_uint32),
                    ("fifo_word", ctypes.c_uint32 * 5), ("fifo_count", ctypes.c_uint32)]
    f5b.argtypes = [ctypes.c_uint32, ctypes.POINTER(P5B)]
    p5b = P5B(); f5b(0x1234, ctypes.byref(p5b))
    assert list(p5b.fifo_word) == [5, 21, 0x8000, 58, 0x1234]
    assert p5b.fifo_count == 5
    class P16B(ctypes.Structure):
        _fields_ = [
            ("computed_word", ctypes.c_uint32),
            ("primary_word", ctypes.c_uint32),
            ("secondary_word", ctypes.c_uint32),
            ("xor_source", ctypes.c_uint32 * 2),
            ("auxiliary_word", ctypes.c_uint32),
            ("xor_mask", ctypes.c_uint32),
            ("fifo_word", ctypes.c_uint32 * 16),
            ("fifo_count", ctypes.c_uint32),
        ]
    f16b = dll.recovered_geometry_packet_951ec
    f16b.argtypes = [ctypes.c_uint32] * 7 + [ctypes.POINTER(P16B)]
    p16b = P16B(); f16b(0x101, 0x202, 0x303, 0x12345678, 0xabcdef01,
                       0x8000, 0x77, ctypes.byref(p16b))
    assert list(p16b.fifo_word) == [6, 5, 18, 0x101, 0x202, 0x303, 21, 0x4000,
                                    47, 0x1234d678, 0x77, 0xabcd6f01, 19,
                                    0x3e4ccccd, 0x3e4ccccd, 0x3e4ccccd]
    assert p16b.fifo_count == 16
    class P11(ctypes.Structure):
        _fields_ = [("input_word", ctypes.c_uint32 * 3), ("packed_word", ctypes.c_uint32),
                    ("fifo_word", ctypes.c_uint32 * 11), ("fifo_count", ctypes.c_uint32)]
    f11 = dll.recovered_geometry_packet_95360
    f11.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32, ctypes.POINTER(P11)]
    p11 = P11(); f11(words, 0xfeedcafe, ctypes.byref(p11))
    assert list(p11.fifo_word) == [5, 18, 10, 20, 30, 21, 0xcafe, 19,
                                   0x3e4ccccd, 0x3e4ccccd, 0x3e4ccccd]
    assert p11.fifo_count == 11
    fixed_95360_callers = [
        (0xc12ccccd, 0x42293333, 0x3f8ccccd, 0xffffd820), # 0x96908
        (0x40333333, 0x41cf3333, 0x00000000, 0xffff8000), # 0x96928
        (0xc1066666, 0x42226666, 0x00000000, 0xffffd820), # 0x96f68
        (0x406ccccd, 0x41e9999a, 0xc0466666, 0xffff8000), # 0x96f8c
        (0xc06ccccd, 0x41ec0000, 0xbfa66666, 0x00000000), # 0x97274
        (0x4112cccd, 0x41b80000, 0x3fc00000, 0xffff8780), # 0x977c8
        (0xc120978d, 0x41dc0000, 0xc100e560, 0x00003c80), # 0x977ec
        (0x410e6666, 0x421a6666, 0x3f4ccccd, 0xffffa200), # 0x98adc
        (0xc0c33333, 0x41db3333, 0x3f333333, 0x00001600), # 0x98f58
        (0x40833333, 0x41e5999a, 0x4089999a, 0xffff9700), # 0x99234
        (0xc0b33333, 0x41c4cccd, 0xc06ccccd, 0x00001200), # 0x992e0
    ]
    for g0, g1, g2, g3 in fixed_95360_callers:
        caller_words = (ctypes.c_uint32 * 3)(g0, g1, g2)
        f11(caller_words, g3, ctypes.byref(p11))
        assert list(p11.fifo_word) == [5, 18, g0, g1, g2, 21,
                                       g3 & 0xffff, 19,
                                       0x3e4ccccd, 0x3e4ccccd,
                                       0x3e4ccccd], hex(g0)
        assert p11.fifo_count == 11
    class P5C(ctypes.Structure):
        _fields_ = [("fifo_word", ctypes.c_uint32 * 5), ("fifo_count", ctypes.c_uint32)]
    f5c = dll.recovered_geometry_packet_95c20
    f5c.argtypes = [ctypes.POINTER(P5C)]
    p5c = P5C(); f5c(ctypes.byref(p5c))
    assert list(p5c.fifo_word) == [5, 21, 0x8000, 5, 58]
    assert p5c.fifo_count == 5
    class W4(ctypes.Structure):
        _fields_ = [("window_word", (ctypes.c_uint32 * 4) * 4),
                    ("window_count", ctypes.c_uint32),
                    ("control_address", ctypes.c_uint32),
                    ("control_value", ctypes.c_uint32),
                    ("publish_address", ctypes.c_uint32),
                    ("helper_target", ctypes.c_uint32),
                    ("helper_call_count", ctypes.c_uint32)]
    w4 = W4(); fw = dll.recovered_geometry_window_95c80
    fw.argtypes = [ctypes.c_uint32, ctypes.POINTER(W4)]
    fw(0x1234, ctypes.byref(w4))
    assert [list(w4.window_word[i]) for i in range(4)] == [
        [0x401e08, 0x401e50, 0x84e1d1, 0],
        [0x401e5c, 0x401e9c, 0x84e232, 0],
        [0x401ea4, 0x401ebc, 0x84e289, 0],
        [0x401ec0, 0x401f78, 0x84e2ae, 0x1234]]
    assert (w4.window_count, w4.control_address, w4.control_value,
            w4.publish_address, w4.helper_target, w4.helper_call_count) == \
           (4, 0x800010, 0x101, 0x804000, 0x6fec0, 4)
    class P10C(ctypes.Structure):
        _fields_ = [("frame_readback", ctypes.c_uint32),
                    ("fifo_word", ctypes.c_uint32 * 10), ("fifo_count", ctypes.c_uint32)]
    f10c = dll.recovered_geometry_packet_95db4
    f10c.argtypes = [ctypes.c_uint32, ctypes.POINTER(P10C)]
    p10c = P10C(); f10c(0xabcdef01, ctypes.byref(p10c))
    assert list(p10c.fifo_word) == [6, 5, 18, 0x413e7803, 0xc0c66666,
                                    0xc0828db9, 21, 0x10000, 58, 0xabcdef01]
    assert p10c.fifo_count == 10
    class P6C(ctypes.Structure):
        _fields_ = [("frame_readback", ctypes.c_uint32),
                    ("fifo_word", ctypes.c_uint32 * 6), ("fifo_count", ctypes.c_uint32)]
    f6c = dll.recovered_geometry_packet_95e90
    f6c.argtypes = [ctypes.c_uint32, ctypes.POINTER(P6C)]
    p6c = P6C(); f6c(0x12345678, ctypes.byref(p6c))
    assert list(p6c.fifo_word) == [6, 5, 21, 0x8000, 58, 0x12345678]
    assert p6c.fifo_count == 6
    class P8F(ctypes.Structure):
        _fields_ = [("frame_readback", ctypes.c_uint32),
                    ("fifo_word", ctypes.c_uint32 * 8), ("fifo_count", ctypes.c_uint32)]
    f8f = dll.recovered_geometry_packet_95f1c
    f8f.argtypes = [ctypes.c_uint32, ctypes.POINTER(P8F)]
    p8f = P8F(); f8f(0x87654321, ctypes.byref(p8f))
    assert list(p8f.fifo_word) == [6, 5, 18, 0x3f8ccccd, 0xc00ccccd,
                                   0xc0800000, 58, 0x87654321]
    assert p8f.fifo_count == 8
    class W2F(ctypes.Structure):
        _fields_ = [("window_word", (ctypes.c_uint32 * 4) * 2),
                    ("window_count", ctypes.c_uint32),
                    ("control_address", ctypes.c_uint32),
                    ("control_value", ctypes.c_uint32),
                    ("publish_address", ctypes.c_uint32)]
    w2f = W2F(); fw2 = dll.recovered_geometry_window_95fac
    fw2.argtypes = [ctypes.c_uint32, ctypes.POINTER(W2F)]
    fw2(0x55aa, ctypes.byref(w2f))
    assert [list(w2f.window_word[i]) for i in range(2)] == [
        [0x40368c, 0x4037e0, 0x84feed, 0x55aa],
        [0x404a64, 0x404ac4, 0x851590, 0x55aa]]
    assert (w2f.window_count, w2f.control_address, w2f.control_value,
            w2f.publish_address) == (2, 0x800010, 0x101, 0x804000)
    w2a = W2F(); fwa = dll.recovered_geometry_window_964a0
    fwa.argtypes = [ctypes.c_uint32, ctypes.POINTER(W2F)]
    fwa(0xcafe, ctypes.byref(w2a))
    assert [list(w2a.window_word[i]) for i in range(2)] == [
        [0x402218, 0x4022c8, 0x84e6bf, 0xcafe],
        [0x4029bc, 0x4029ec, 0x84efca, 0xcafe]]
    assert (w2a.window_count, w2a.control_address, w2a.control_value,
            w2a.publish_address) == (2, 0x800010, 0x101, 0x804000)
    class P97E10C(ctypes.Structure):
        _fields_ = [("table_word", ctypes.c_uint32 * 3),
                    ("context_word", ctypes.c_uint32),
                    ("derived_word", ctypes.c_uint32),
                    ("fifo_word", ctypes.c_uint32 * 12),
                    ("fifo_count", ctypes.c_uint32)]
    f97e10 = dll.recovered_geometry_packet_97e10
    f97e10.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32,
                       ctypes.POINTER(P97E10C)]
    table = (ctypes.c_uint32 * 3)(0x11, 0x22, 0x33)
    p97e10 = P97E10C(); f97e10(table, 0x240, ctypes.byref(p97e10))
    assert list(p97e10.fifo_word) == [5, 18, 0x11, 0x22, 0x33, 21,
                                      0xfdc0, 19, 0x3e800000,
                                      0x3f800000, 0x3f800000, 58]
    assert (p97e10.context_word, p97e10.derived_word,
            p97e10.fifo_count) == (0x240, 0xfdc0, 12)
    class P982F8C(ctypes.Structure):
        _fields_ = [("response_word", ctypes.c_uint32 * 3),
                    ("context_word", ctypes.c_uint32),
                    ("derived_word", ctypes.c_uint32),
                    ("fifo_word", ctypes.c_uint32 * 11),
                    ("fifo_count", ctypes.c_uint32)]
    f982f8 = dll.recovered_geometry_packet_982f8
    f982f8.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(P982F8C)]
    p982f8 = P982F8C(); f982f8(0x101, 0x202, 0x303, 0x240,
                               ctypes.byref(p982f8))
    assert list(p982f8.fifo_word) == [18, 0x101, 0x202, 0x303, 21,
                                      0xfdc0, 19, 0x3f88f5c3,
                                      0x3f800000, 0x3f800000, 58]
    assert (p982f8.context_word, p982f8.derived_word,
            p982f8.fifo_count) == (0x240, 0xfdc0, 11)
print("recovered geometry 0x938d0 packet/window: ok")
