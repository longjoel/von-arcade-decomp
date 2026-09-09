#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_diagnostic_variant_b_8f010.c"

class Input(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "record_word", "payload_word_0", "payload_word_1", "raw_word_0",
        "raw_word_1", "raw_word_2", "frame_readback")]
class Plan(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32 * 15), ("fifo_count", ctypes.c_uint32),
                ("masked_word_0", ctypes.c_uint32), ("masked_word_1", ctypes.c_uint32),
                ("masked_word_2", ctypes.c_uint32)]
class LoopPlan(ctypes.Structure):
    _fields_ = [("state_word", ctypes.c_uint32), ("window_word", ctypes.c_uint32 * 4),
                ("control_address", ctypes.c_uint32), ("control_value", ctypes.c_uint32),
                ("next_record_pointer", ctypes.c_uint32), ("record_endpoint", ctypes.c_uint32),
                ("next_aux_pointer", ctypes.c_uint32), ("next_record_stride", ctypes.c_uint32),
                ("loop_continues", ctypes.c_uint32), ("terminal_completion", ctypes.c_uint32)]
class Packet9Plan(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32 * 9), ("fifo_count", ctypes.c_uint32),
                ("frame_word", ctypes.c_uint32), ("frame_readback", ctypes.c_uint32)]
class WindowCPlan(ctypes.Structure):
    _fields_ = [("state_word", ctypes.c_uint32), ("window_word", ctypes.c_uint32 * 4),
                ("control_address", ctypes.c_uint32), ("control_value", ctypes.c_uint32),
                ("next_target", ctypes.c_uint32)]
class FixedCPlan(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32 * 11), ("fifo_count", ctypes.c_uint32),
                ("frame_readback", ctypes.c_uint32)]
class FinalCPlan(ctypes.Structure):
    _fields_ = [("state_word", ctypes.c_uint32), ("window_word", ctypes.c_uint32 * 4),
                ("control_address", ctypes.c_uint32), ("control_value", ctypes.c_uint32),
                ("completion_word", ctypes.c_uint32 * 2)]
class LoopEPlan(ctypes.Structure):
    _fields_ = [("current_record_pointer", ctypes.c_uint32), ("current_aux_pointer", ctypes.c_uint32),
                ("next_record_pointer", ctypes.c_uint32), ("next_aux_pointer", ctypes.c_uint32),
                ("record_endpoint", ctypes.c_uint32), ("next_record_stride", ctypes.c_uint32),
                ("loop_continues", ctypes.c_uint32), ("completion_word", ctypes.c_uint32)]
class WindowEPlan(ctypes.Structure):
    _fields_ = [("state_word", ctypes.c_uint32), ("window_word", ctypes.c_uint32 * 4),
                ("control_address", ctypes.c_uint32), ("control_value", ctypes.c_uint32),
                ("completion_word", ctypes.c_uint32 * 2), ("return_address", ctypes.c_uint32)]
class PacketEPlan(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32 * 7), ("fifo_count", ctypes.c_uint32),
                ("frame_word", ctypes.c_uint32), ("frame_readback", ctypes.c_uint32)]
class PacketFPlan(ctypes.Structure):
    _fields_ = [("record_word", ctypes.c_uint32), ("payload_word_0", ctypes.c_uint32),
                ("payload_word_1", ctypes.c_uint32), ("raw_word_0", ctypes.c_uint32),
                ("raw_word_1", ctypes.c_uint32), ("raw_word_2", ctypes.c_uint32),
                ("masked_word_0", ctypes.c_uint32), ("masked_word_1", ctypes.c_uint32),
                ("masked_word_2", ctypes.c_uint32),
                ("fifo_word", ctypes.c_uint32 * 14), ("fifo_count", ctypes.c_uint32)]
class WindowFPlan(ctypes.Structure):
    _fields_ = [("state_word", ctypes.c_uint32), ("window_word", ctypes.c_uint32 * 4),
                ("control_address", ctypes.c_uint32), ("control_value", ctypes.c_uint32),
                ("publish_address", ctypes.c_uint32)]
class LoopFPlan(ctypes.Structure):
    _fields_ = [("current_record_pointer", ctypes.c_uint32),
                ("current_aux_pointer", ctypes.c_uint32),
                ("next_record_pointer", ctypes.c_uint32),
                ("next_aux_pointer", ctypes.c_uint32),
                ("record_endpoint", ctypes.c_uint32),
                ("next_record_stride", ctypes.c_uint32),
                ("loop_continues", ctypes.c_uint32),
                ("completion_word", ctypes.c_uint32)]
class PacketGPlan(ctypes.Structure):
    _fields_ = [("input_word", ctypes.c_uint32),
                ("fifo_word", ctypes.c_uint32 * 6), ("fifo_count", ctypes.c_uint32)]
class WindowGPlan(ctypes.Structure):
    _fields_ = [("state_word", ctypes.c_uint32), ("mode_word", ctypes.c_uint32),
                ("frame_word", ctypes.c_uint32), ("window_word", ctypes.c_uint32 * 4),
                ("control_address", ctypes.c_uint32), ("control_value", ctypes.c_uint32),
                ("publish_address", ctypes.c_uint32),
                ("completion_word", ctypes.c_uint32 * 2)]
class WindowDPlan(ctypes.Structure):
    _fields_ = [("state_word", ctypes.c_uint32), ("window_word", ctypes.c_uint32 * 4),
                ("control_address", ctypes.c_uint32), ("control_value", ctypes.c_uint32),
                ("next_target", ctypes.c_uint32)]
class LoopDPlan(ctypes.Structure):
    _fields_ = [("current_record_pointer", ctypes.c_uint32),
                ("current_aux_pointer", ctypes.c_uint32),
                ("next_record_pointer", ctypes.c_uint32), ("next_aux_pointer", ctypes.c_uint32),
                ("record_endpoint", ctypes.c_uint32), ("next_record_stride", ctypes.c_uint32),
                ("loop_continues", ctypes.c_uint32), ("terminal_completion", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "diagnostic_variant_b.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_b_8f010
    fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    sample = Input(0x11111111, 0x22222222, 0x33333333,
                   0xaaaa0001, 0xbbbb0002, 0xcccc0003, 0xdeadbeef)
    plan = Plan(); fn(ctypes.byref(sample), ctypes.byref(plan))
    assert list(plan.fifo_word) == [5, 19, 0x40000000, 0x40000000, 0x40000000,
                                    5, 44, 0x11111111, 0x22222222, 0x33333333,
                                    1, 2, 3, 58, 0xdeadbeef]
    assert plan.fifo_count == 15
    assert (plan.masked_word_0, plan.masked_word_1, plan.masked_word_2) == (1, 2, 3)
    variant_c_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_c_8f1f0
    variant_c_fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    variant_c = Plan(); variant_c_fn(ctypes.byref(sample), ctypes.byref(variant_c))
    assert list(variant_c.fifo_word) == list(plan.fifo_word)
    assert variant_c.fifo_count == 15
    variant_d_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_d_8f620
    variant_d_fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    variant_d = Plan(); variant_d_fn(ctypes.byref(sample), ctypes.byref(variant_d))
    assert list(variant_d.fifo_word) == [5, 19, 0x3fd9999a, 0x3fd9999a,
                                         0x3fd9999a, 5, 44, 0x11111111,
                                         0x22222222, 0x33333333, 1, 2, 3, 58,
                                         0xdeadbeef]
    assert variant_d.fifo_count == 15
    window_d_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_d_window_8f730
    window_d_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
                            ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32,
                            ctypes.POINTER(WindowDPlan)]
    zero_d = (ctypes.c_uint32 * 3)(1, 2, 3)
    nonzero_d = (ctypes.c_uint32 * 3)(4, 5, 6)
    window_d = WindowDPlan(); window_d_fn(0, zero_d, nonzero_d, 0x1234, ctypes.byref(window_d))
    assert list(window_d.window_word) == [1, 2, 3, 0]
    assert (window_d.control_address, window_d.control_value, window_d.next_target) == (
        0x800010, 0x101, 0x8f7d4)
    window_d_fn(1, zero_d, nonzero_d, 0x1234, ctypes.byref(window_d))
    assert list(window_d.window_word) == [4, 5, 6, 0x1234]
    loop_d_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_d_loop_8f7d4
    loop_d_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(LoopDPlan)]
    loop_d = LoopDPlan(); loop_d_fn(0x142b68, 0x142b40, ctypes.byref(loop_d))
    assert (loop_d.next_record_pointer, loop_d.next_aux_pointer,
            loop_d.record_endpoint, loop_d.loop_continues,
            loop_d.terminal_completion) == (0x142b94, 0x142b6c, 0x142b94, 1, 0)
    loop_d_fn(0x142b94, 0x142b68, ctypes.byref(loop_d))
    assert (loop_d.loop_continues, loop_d.terminal_completion) == (0, 6)
    loop_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_b_loop_8f120
    loop_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
                        ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32,
                        ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(LoopPlan)]
    zero = (ctypes.c_uint32 * 3)(1, 2, 3)
    nonzero = (ctypes.c_uint32 * 3)(4, 5, 6)
    loop = LoopPlan()
    loop_fn(0, zero, nonzero, 0x1234, 0x1424e0, 0x142330, ctypes.byref(loop))
    assert list(loop.window_word) == [1, 2, 3, 0]
    assert (loop.next_record_pointer, loop.next_aux_pointer,
            loop.record_endpoint, loop.next_record_stride,
            loop.loop_continues, loop.terminal_completion) == (
                0x14250c, 0x14235c, 0x14250c, 0x2c, 1, 0)
    loop_fn(1, zero, nonzero, 0x1234, 0x14250c, 0x142358, ctypes.byref(loop))
    assert list(loop.window_word) == [4, 5, 6, 0x1234]
    assert (loop.loop_continues, loop.terminal_completion) == (0, 6)
    packet9_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_c_packet_8f3cc
    packet9_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Packet9Plan)]
    packet9 = Packet9Plan(); packet9_fn(0x12345678, 0xdeadbeef, ctypes.byref(packet9))
    assert list(packet9.fifo_word) == [5, 18, 0x12345678, 0x418edaee,
                                       0xbed6a162, 20, 0x441, 44, 0xdeadbeef]
    assert packet9.fifo_count == 9 and packet9.frame_word == 0x12345678
    window_c_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_c_window_8f458
    window_c_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(WindowCPlan)]
    window_c = WindowCPlan(); window_c_fn(0, 0x1234, ctypes.byref(window_c))
    assert list(window_c.window_word) == [0xed0ba, 0xed378, 0xa466a5, 0]
    assert (window_c.control_address, window_c.control_value, window_c.next_target) == (
        0x800010, 0x101, 0x8f4d0)
    window_c_fn(1, 0x1234, ctypes.byref(window_c))
    assert list(window_c.window_word) == [0xed0ba, 0x599a7a, 0xa466a5, 0x1234]
    fixed_c_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_c_fixed_8f4d0
    fixed_c_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(FixedCPlan)]
    fixed_c = FixedCPlan(); fixed_c_fn(0x12345678, 0xdeadbeef, ctypes.byref(fixed_c))
    assert list(fixed_c.fifo_word) == [6, 5, 44, 0x4019999a, 0x12345678,
                                       0x3f333333, 0x11e, 0xf8ce, 0xfccf,
                                       44, 0xdeadbeef]
    assert fixed_c.fifo_count == 11
    final_c_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_c_final_8f57c
    final_c_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(FinalCPlan)]
    final_c = FinalCPlan(); final_c_fn(0, 0x1234, ctypes.byref(final_c))
    assert list(final_c.window_word) == [0x402f58, 0x403138, 0x84f601, 0x1234]
    assert (final_c.control_address, final_c.control_value,
            list(final_c.completion_word)) == (0x800010, 0x101, [6, 6])
    final_c_fn(1, 0x1234, ctypes.byref(final_c))
    assert list(final_c.window_word) == [0x402f58, 0x5afdda, 0x84f601, 0x1234]
    variant_e_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_e_90540
    variant_e_fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    variant_e = Plan(); variant_e_fn(ctypes.byref(sample), ctypes.byref(variant_e))
    assert list(variant_e.fifo_word) == list(plan.fifo_word) and variant_e.fifo_count == 15
    loop_e_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_e_loop_90590
    loop_e_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(LoopEPlan)]
    loop_e = LoopEPlan(); loop_e_fn(0x14266c, 0x142644, ctypes.byref(loop_e))
    assert (loop_e.next_record_pointer, loop_e.next_aux_pointer, loop_e.record_endpoint,
            loop_e.next_record_stride, loop_e.loop_continues, loop_e.completion_word) == (
                0x142698, 0x142670, 0x1427a0, 0x2c, 1, 6)
    packet_e_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_e_packet_9070c
    packet_e_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(PacketEPlan)]
    packet_e = PacketEPlan(); packet_e_fn(0x12345678, 0xdeadbeef, ctypes.byref(packet_e))
    assert list(packet_e.fifo_word) == [5, 18, 0x12345678, 0x4187f454,
                                        0x3f0346dc, 58, 0xdeadbeef]
    assert packet_e.fifo_count == 7 and packet_e.frame_word == 0x12345678
    packet_f_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_f_packet_908a0
    packet_f_fn.argtypes = [ctypes.c_uint32] * 6 + [ctypes.POINTER(PacketFPlan)]
    packet_f = PacketFPlan()
    packet_f_fn(0x11111111, 0x22222222, 0x33333333,
                0xaaaa0001, 0xbbbb0002, 0xcccc0003, ctypes.byref(packet_f))
    assert list(packet_f.fifo_word) == [5, 19, 0x40000000, 0x40000000,
                                        0x40000000, 5, 44, 0x11111111,
                                        0x22222222, 0x33333333, 1, 2, 3, 58]
    assert (packet_f.masked_word_0, packet_f.masked_word_1,
            packet_f.masked_word_2, packet_f.fifo_count) == (1, 2, 3, 14)
    window_f_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_f_window_90994
    window_f_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
                            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(WindowFPlan)]
    zero_f = (ctypes.c_uint32 * 3)(1, 2, 3)
    nonzero_f = (ctypes.c_uint32 * 3)(4, 5, 6)
    window_f = WindowFPlan(); window_f_fn(0, zero_f, nonzero_f, ctypes.byref(window_f))
    assert list(window_f.window_word) == [1, 2, 3, 0]
    assert (window_f.control_address, window_f.control_value, window_f.publish_address) == (
        0x800010, 0, 0x804000)
    window_f_fn(0x1234, zero_f, nonzero_f, ctypes.byref(window_f))
    assert list(window_f.window_word) == [4, 5, 6, 0]
    assert window_f.control_value == 0x1234
    loop_f_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_f_loop_90a58
    loop_f_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(LoopFPlan)]
    loop_f = LoopFPlan(); loop_f_fn(0x142da4, 0x142d78, ctypes.byref(loop_f))
    assert (loop_f.next_record_pointer, loop_f.next_aux_pointer,
            loop_f.record_endpoint, loop_f.next_record_stride,
            loop_f.loop_continues, loop_f.completion_word) == (
                0x142dd0, 0x142da4, 0x142dd0, 0x2c, 1, 6)
    loop_f_fn(0x142dd0, 0x142da4, ctypes.byref(loop_f))
    assert loop_f.loop_continues == 0
    packet_g_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_g_packet_90a7c
    packet_g_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(PacketGPlan)]
    packet_g = PacketGPlan(); packet_g_fn(0x12345678, ctypes.byref(packet_g))
    assert list(packet_g.fifo_word) == [5, 18, 0x12345678,
                                        0x41900000, 0xbf800000, 58]
    assert packet_g.fifo_count == 6
    window_g_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_g_window_90af8
    window_g_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                            *([ctypes.POINTER(ctypes.c_uint32)] * 4),
                            ctypes.POINTER(WindowGPlan)]
    s0m0 = (ctypes.c_uint32 * 3)(1, 2, 3)
    s1m0 = (ctypes.c_uint32 * 3)(4, 5, 6)
    s0m1 = (ctypes.c_uint32 * 3)(7, 8, 9)
    s1m1 = (ctypes.c_uint32 * 3)(10, 11, 12)
    window_g = WindowGPlan()
    window_g_fn(0, 0, 0x1234, s0m0, s1m0, s0m1, s1m1, ctypes.byref(window_g))
    assert list(window_g.window_word) == [1, 2, 3, 0]
    window_g_fn(1, 0, 0x1234, s0m0, s1m0, s0m1, s1m1, ctypes.byref(window_g))
    assert list(window_g.window_word) == [4, 5, 6, 0]
    window_g_fn(0, 1, 0x1234, s0m0, s1m0, s0m1, s1m1, ctypes.byref(window_g))
    assert list(window_g.window_word) == [7, 8, 9, 0x1234]
    window_g_fn(1, 1, 0x1234, s0m0, s1m0, s0m1, s1m1, ctypes.byref(window_g))
    assert (list(window_g.window_word), list(window_g.completion_word)) == ([10, 11, 12, 0x1234], [6, 6])
    window_e_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_e_window_90788
    window_e_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(WindowEPlan)]
    window_e = WindowEPlan(); window_e_fn(0, 0x1234, ctypes.byref(window_e))
    assert list(window_e.window_word) == [0x4029f4, 0x402e34, 0x84f00d, 0]
    assert (list(window_e.completion_word), window_e.return_address) == ([6, 6], 0x9089c)
    window_e_fn(1, 0x1234, ctypes.byref(window_e))
    assert list(window_e.window_word) == [0x4029f4, 0x5afcbe, 0x84f00d, 0x1234]
print("recovered geometry 0x8f010 diagnostic-variant-b prefix: ok")
