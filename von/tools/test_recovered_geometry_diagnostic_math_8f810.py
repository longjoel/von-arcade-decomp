#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_diagnostic_math_8f810.c"

class Plan(ctypes.Structure):
    _fields_ = [("source_halfword", ctypes.c_uint32), ("normalized_source", ctypes.c_uint32),
                ("initial_word", ctypes.c_uint32), ("response_word", ctypes.c_uint32),
                ("computed_word", ctypes.c_uint32), ("fifo_word", ctypes.c_uint32 * 15),
                ("fifo_count", ctypes.c_uint32), ("frame_readback", ctypes.c_uint32)]
class Packet9Plan(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32 * 9), ("fifo_count", ctypes.c_uint32),
                ("computed_word", ctypes.c_uint32), ("frame_readback", ctypes.c_uint32)]
class WindowMathPlan(ctypes.Structure):
    _fields_ = [("state_word", ctypes.c_uint32), ("window_word", ctypes.c_uint32 * 4),
                ("control_address", ctypes.c_uint32), ("control_value", ctypes.c_uint32),
                ("completion_word", ctypes.c_uint32), ("call_target", ctypes.c_uint32)]
class PostServicePlan(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32 * 10), ("fifo_count", ctypes.c_uint32),
                ("masked_word_0", ctypes.c_uint32), ("masked_word_1", ctypes.c_uint32),
                ("masked_word_2", ctypes.c_uint32), ("frame_readback", ctypes.c_uint32)]
class SetupPlan(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32 * 8), ("fifo_count", ctypes.c_uint32),
                ("frame_word", ctypes.c_uint32)]
class SecondPlan(ctypes.Structure):
    _fields_ = [("source_halfword", ctypes.c_uint32), ("normalized_source", ctypes.c_uint32),
                ("initial_word", ctypes.c_uint32), ("response_word", ctypes.c_uint32),
                ("computed_word", ctypes.c_uint32), ("fifo_word", ctypes.c_uint32 * 13),
                ("fifo_count", ctypes.c_uint32), ("frame_readback", ctypes.c_uint32)]
class SecondWindowPlan(ctypes.Structure):
    _fields_ = [("state_word", ctypes.c_uint32), ("window_word", ctypes.c_uint32 * 4),
                ("control_address", ctypes.c_uint32), ("control_value", ctypes.c_uint32),
                ("next_target", ctypes.c_uint32)]
class TerminalPlan(ctypes.Structure):
    _fields_ = [("source_halfword", ctypes.c_uint32), ("normalized_source", ctypes.c_uint32),
                ("initial_word", ctypes.c_uint32), ("computed_word", ctypes.c_uint32),
                ("frame_readback", ctypes.c_uint32), ("fifo_word", ctypes.c_uint32 * 14),
                ("fifo_count", ctypes.c_uint32)]
class ThirdWindowPlan(ctypes.Structure):
    _fields_ = [("state_word", ctypes.c_uint32), ("window_word", ctypes.c_uint32 * 4),
                ("control_address", ctypes.c_uint32), ("control_value", ctypes.c_uint32),
                ("publish_address", ctypes.c_uint32), ("completion_word", ctypes.c_uint32)]
class ThirdSetupPlan(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32 * 8), ("fifo_count", ctypes.c_uint32),
                ("frame_word", ctypes.c_uint32)]
class ThirdPlan(ctypes.Structure):
    _fields_ = [("source_halfword", ctypes.c_uint32), ("normalized_source", ctypes.c_uint32),
                ("initial_word", ctypes.c_uint32), ("response_word", ctypes.c_uint32),
                ("computed_word", ctypes.c_uint32), ("fifo_word", ctypes.c_uint32 * 15),
                ("fifo_count", ctypes.c_uint32), ("frame_readback", ctypes.c_uint32)]
class ThirdWindow90124Plan(ctypes.Structure):
    _fields_ = [("state_word", ctypes.c_uint32), ("window_word", ctypes.c_uint32 * 4),
                ("control_address", ctypes.c_uint32), ("control_value", ctypes.c_uint32),
                ("publish_address", ctypes.c_uint32), ("completion_word", ctypes.c_uint32),
                ("call_target", ctypes.c_uint32)]
class RecordPacket90398Plan(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32 * 10), ("fifo_count", ctypes.c_uint32),
                ("masked_word_0", ctypes.c_uint32), ("masked_word_1", ctypes.c_uint32),
                ("masked_word_2", ctypes.c_uint32), ("frame_readback", ctypes.c_uint32)]
class RecordWindow9044cPlan(ctypes.Structure):
    _fields_ = [("state_word", ctypes.c_uint32), ("window_word", ctypes.c_uint32 * 4),
                ("zero_word", ctypes.c_uint32 * 3), ("nonzero_word", ctypes.c_uint32 * 3),
                ("control_address", ctypes.c_uint32), ("control_value", ctypes.c_uint32),
                ("publish_address", ctypes.c_uint32)]
class RecordLoop904f4Plan(ctypes.Structure):
    _fields_ = [("primary_start", ctypes.c_uint32), ("auxiliary_start", ctypes.c_uint32),
                ("primary_end", ctypes.c_uint32), ("auxiliary_end", ctypes.c_uint32),
                ("stride", ctypes.c_uint32), ("iterations", ctypes.c_uint32),
                ("completion_count", ctypes.c_uint32), ("return_address", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "diagnostic_math.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_math_8f810
    fn.argtypes = [ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32,
                   ctypes.c_uint32, ctypes.POINTER(Plan)]
    plan = Plan(); fn(0x253 + 3, 0x12345678, 0xabcdef01,
                      0xdeadbeef, ctypes.byref(plan))
    assert (plan.normalized_source, plan.initial_word) == (3, 3 << 7)
    assert list(plan.fifo_word) == [5, 27, 3 << 7, 27, 3 << 7, 18, 0,
                                    0xabcdef01, 0, 18, 0, 0xbf800000, 0, 58,
                                    0xdeadbeef]
    assert plan.response_word == 0x12345678 and plan.fifo_count == 15
    fn(0x252, 0, 0, 0, ctypes.byref(plan))
    assert (plan.normalized_source, plan.initial_word) == (0x1ff, 0xff80)
    packet_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_math_packet_8f928
    packet_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Packet9Plan)]
    packet = Packet9Plan(); packet_fn(0xabcdef01, 0xdeadbeef, ctypes.byref(packet))
    assert list(packet.fifo_word) == [5, 44, 0xbfe820c5, 0x4189f8a1, 0x3f6c7e28,
                                      0x3c0f, 0xdfc5, 0xabcdef01, 0xdeadbeef]
    assert packet.fifo_count == 9 and packet.computed_word == 0xabcdef01
    window_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_math_window_8f9d0
    window_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(WindowMathPlan)]
    window = WindowMathPlan(); window_fn(0, 0x1234, ctypes.byref(window))
    assert list(window.window_word) == [0x12a7ee, 0x12a80e, 0xa8b135, 0]
    assert (window.control_address, window.control_value,
            window.completion_word, window.call_target) == (0x800010, 0x101, 6, 0x6fec0)
    window_fn(1, 0x1234, ctypes.byref(window))
    assert list(window.window_word) == [0x12b8fc, 0x5a36f2, 0xa8c5fc, 0x1234]
    post_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_math_post_service_8fa78
    post_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.c_uint32, ctypes.POINTER(PostServicePlan)]
    post = PostServicePlan()
    post_fn(0x11111111, 0x22222222, 0x33333333, 0xaaaa0001,
            0xbbbb0002, 0xcccc0003, 0xdeadbeef, ctypes.byref(post))
    assert list(post.fifo_word) == [5, 44, 0x11111111, 0x22222222, 0x33333333,
                                    1, 2, 3, 58, 0xdeadbeef]
    assert post.fifo_count == 10 and post.frame_readback == 0xdeadbeef
    setup_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_math_setup_8fbf4
    setup_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(SetupPlan)]
    setup = SetupPlan(); setup_fn(0x12345678, ctypes.byref(setup))
    assert list(setup.fifo_word) == [5, 44, 0x12345678, 0x419993a9,
                                     0xbdb39c0f, 0xf099, 0x12345678, 0x12345678]
    assert setup.fifo_count == 8 and setup.frame_word == 0x12345678
    second_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_math_second_8fc54
    second_fn.argtypes = [ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32,
                          ctypes.c_uint32, ctypes.POINTER(SecondPlan)]
    second = SecondPlan(); second_fn(0x256, 0x12345678, 0xabcdef01,
                                     0xdeadbeef, ctypes.byref(second))
    assert (second.normalized_source, second.initial_word) == (3, 3 << 7)
    assert list(second.fifo_word) == [5, 18, 0xbf800000, 0x40000000,
                                      0xbe800000, 27, 3 << 7, 27, 3 << 7,
                                      20, 0xabcdef01, 58, 0xdeadbeef]
    assert second.fifo_count == 13 and second.response_word == 0x12345678
    second_window_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_math_second_window_8fd64
    second_window_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                                 ctypes.POINTER(SecondWindowPlan)]
    second_window = SecondWindowPlan(); second_window_fn(0, 0x1234, ctypes.byref(second_window))
    assert list(second_window.window_word) == [0x12d368, 0x12d3b0, 0xa8e799, 0x1234]
    assert (second_window.control_address, second_window.control_value,
            second_window.next_target) == (0x800010, 0x101, 0x8fddc)
    second_window_fn(1, 0x1234, ctypes.byref(second_window))
    assert list(second_window.window_word) == [0x12d368, 0x5a3a32, 0xa8e799, 0x1234]
    terminal_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_math_terminal_8fdf0
    terminal_fn.argtypes = [ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.POINTER(TerminalPlan)]
    terminal = TerminalPlan(); terminal_fn(0x256, 0xabcdef01, 0xdeadbeef,
                                           ctypes.byref(terminal))
    assert (terminal.normalized_source, terminal.initial_word) == (3, 3 << 7)
    assert list(terminal.fifo_word) == [6, 5, 18, 0xbf800000, 0x40000000,
                                       0xbe800000, 27, 3 << 7, 27, 3 << 7,
                                       20, 0xabcdef01, 58, 0xdeadbeef]
    assert terminal.fifo_count == 14
    third_window_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_math_third_window_8ff00
    third_window_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                                ctypes.POINTER(ThirdWindowPlan)]
    third_window = ThirdWindowPlan(); third_window_fn(0, 0x1234, ctypes.byref(third_window))
    assert list(third_window.window_word) == [0x12d3b4, 0x12d3fc, 0xa8e818, 0]
    assert (third_window.control_address, third_window.control_value,
            third_window.publish_address, third_window.completion_word) == (0x800010, 0x101,
                                                                             0x804000, 6)
    third_window_fn(1, 0x1234, ctypes.byref(third_window))
    assert list(third_window.window_word) == [0x12d3b4, 0x5a3a36, 0xa8e818, 0x1234]
    third_setup_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_math_third_setup_8ff98
    third_setup_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(ThirdSetupPlan)]
    third_setup = ThirdSetupPlan(); third_setup_fn(0x12345678, ctypes.byref(third_setup))
    assert list(third_setup.fifo_word) == [5, 44, 0x12345678, 0x415c7ae1,
                                           0xbfe66666, 0x71, 0x12345678, 0x12345678]
    assert third_setup.fifo_count == 8 and third_setup.frame_word == 0x12345678
    third_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_math_third_8fff4
    third_fn.argtypes = [ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.POINTER(ThirdPlan)]
    third = ThirdPlan(); third_fn(0x256, 0x12345678, 0xabcdef01,
                                  0xdeadbeef, ctypes.byref(third))
    assert (third.normalized_source, third.initial_word) == (3, 3 << 7)
    assert list(third.fifo_word) == [5, 18, 0xbf000000, 0x3f800000, 0xbfa66666,
                                    21, 0xfffff800, 27, 3 << 7, 27, 3 << 7,
                                    20, 0xabcdef01, 58, 0xdeadbeef]
    assert third.response_word == 0x12345678 and third.fifo_count == 15
    third_window_90124_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_math_third_window_90124
    third_window_90124_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                                      ctypes.POINTER(ThirdWindow90124Plan)]
    third_window_90124 = ThirdWindow90124Plan()
    third_window_90124_fn(0, 0x1234, ctypes.byref(third_window_90124))
    assert list(third_window_90124.window_word) == [0x12d400, 0x12d464, 0xa8e897, 0x1234]
    assert (third_window_90124.control_address, third_window_90124.control_value,
            third_window_90124.publish_address, third_window_90124.completion_word,
            third_window_90124.call_target) == (0x800010, 0x101, 0x804000, 6, 0x6fec0)
    third_window_90124_fn(1, 0x1234, ctypes.byref(third_window_90124))
    assert list(third_window_90124.window_word) == [0x12d400, 0x5a3a3a, 0xa8e897, 0x1234]
    record_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_math_record_packet_90398
    record_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                          ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                          ctypes.c_uint32, ctypes.POINTER(RecordPacket90398Plan)]
    record = RecordPacket90398Plan()
    record_fn(0x11111111, 0x22222222, 0x33333333, 0xaaaa0001,
              0xbbbb0002, 0xcccc0003, 0xdeadbeef, ctypes.byref(record))
    assert list(record.fifo_word) == [5, 44, 0x11111111, 0x22222222, 0x33333333,
                                      1, 2, 3, 58, 0xdeadbeef]
    assert record.fifo_count == 10 and record.masked_word_2 == 3
    window_record_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_math_record_window_9044c
    window_record_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
                                 ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32,
                                 ctypes.POINTER(RecordWindow9044cPlan)]
    zero = (ctypes.c_uint32 * 3)(1, 2, 3); nonzero = (ctypes.c_uint32 * 3)(4, 5, 6)
    window_record = RecordWindow9044cPlan()
    window_record_fn(0, zero, nonzero, 0x1234, ctypes.byref(window_record))
    assert list(window_record.window_word) == [1, 2, 3, 0]
    assert (window_record.control_address, window_record.control_value,
            window_record.publish_address) == (0x800010, 0x101, 0x804000)
    window_record_fn(1, zero, nonzero, 0x1234, ctypes.byref(window_record))
    assert list(window_record.window_word) == [4, 5, 6, 0x1234]
    loop_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_math_record_loop_904f4
    loop_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.POINTER(RecordLoop904f4Plan)]
    loop = RecordLoop904f4Plan(); loop_fn(0x142958, 0x142930, 0x142a60, ctypes.byref(loop))
    assert (loop.primary_end, loop.auxiliary_end, loop.stride,
            loop.iterations, loop.completion_count, loop.return_address) == (
                0x142a8c, 0x142a64, 0x2c, 7, 8, 0x9052c)
    listing = pathlib.Path(root / "von/build/disasm/vonj-maincpu.lst").read_text()
    callsite = listing[listing.index("   985d4:"):listing.index("   985dc:")]
    assert "call\t0x2a990" in callsite
    assert "call\t0x8f810" in callsite
print("recovered geometry 0x8f810 diagnostic-math packet: ok")
