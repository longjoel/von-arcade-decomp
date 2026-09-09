#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_packet_93700.c"

class Plan(ctypes.Structure):
    _fields_ = [
        ("index", ctypes.c_uint32), ("existing_word", ctypes.c_uint32),
        ("existing_negative", ctypes.c_uint32),
        ("helper_input", ctypes.c_uint32 * 2),
        ("helper_result", ctypes.c_uint32 * 2),
        ("helper_target", ctypes.c_uint32),
        ("updated_word", ctypes.c_uint32 * 3),
        ("updated_mask", ctypes.c_uint32 * 3),
        ("packet_target", ctypes.c_uint32),
    ]
class Packet(ctypes.Structure):
    _fields_ = [("table_word", ctypes.c_uint32 * 3),
                ("context_word", ctypes.c_uint32),
                ("derived_word", ctypes.c_uint32),
                ("fifo_word", ctypes.c_uint32 * 12),
                ("fifo_count", ctypes.c_uint32)]
class Loop(ctypes.Structure):
    _fields_ = [("start_index", ctypes.c_uint32),
                ("end_exclusive", ctypes.c_uint32),
                ("iteration_count", ctypes.c_uint32),
                ("packet_preamble", ctypes.c_uint32 * 6),
                ("packet_preamble_count", ctypes.c_uint32),
                ("update_target", ctypes.c_uint32),
                ("packet_target", ctypes.c_uint32),
                ("completion_word", ctypes.c_uint32),
                ("window_word", ctypes.c_uint32 * 4),
                ("control_address", ctypes.c_uint32),
                ("control_value", ctypes.c_uint32)]
class Post(ctypes.Structure):
    _fields_ = [("source_word", ctypes.c_uint32),
                ("source_byte", ctypes.c_uint32),
                ("service_first", ctypes.c_uint32),
                ("service_second", ctypes.c_uint32),
                ("service_target", ctypes.c_uint32),
                ("completion_word", ctypes.c_uint32),
                ("command29", ctypes.c_uint32),
                ("command30", ctypes.c_uint32),
                ("context_word", ctypes.c_uint32),
                ("constant_word", ctypes.c_uint32),
                ("zero_response_word", ctypes.c_uint32),
                ("packet_target", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "indexed-update.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    fn = ctypes.CDLL(str(library)).recovered_geometry_indexed_table_update_97d50
    fn.argtypes = [ctypes.c_uint32] * 5 + [ctypes.POINTER(Plan)]
    plan = Plan()
    fn(3, 0x3f000000, 0x0093, 0x0093, 0x5024e8, ctypes.byref(plan))
    assert plan.existing_negative == 0
    assert list(plan.helper_input) == [0x5024eb, 0x5024eb]
    assert list(plan.updated_word) == [0x3f800000, 0xc1880000, 0x3f800000]
    assert list(plan.updated_mask) == [1, 1, 1]
    assert (plan.helper_target, plan.packet_target) == (0xf5058, 0x97e10)

    fn(3, 0xbf000000, 0x1234, 0x5678, 0x5024e8, ctypes.byref(plan))
    assert plan.existing_negative == 1
    assert list(plan.updated_mask) == [0, 1, 0]
    assert list(plan.updated_word) == [0, 0, 0]

    fn(3, 0x80000000, 0, 0, 0, ctypes.byref(plan))
    assert plan.existing_negative == 0
    fn(3, 0xff800001, 0, 0, 0, ctypes.byref(plan))
    assert plan.existing_negative == 0

    composed = ctypes.CDLL(str(library)).recovered_geometry_indexed_table_update_and_packet_97d50
    composed.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
                         ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.POINTER(Plan),
                         ctypes.POINTER(Packet)]
    existing = (ctypes.c_uint32 * 3)(0x11111111, 0x3f000000, 0x33333333)
    packet = Packet()
    composed(3, existing, 0x0093, 0x0093, 0x5024e8, 0x4567,
             ctypes.byref(plan), ctypes.byref(packet))
    assert list(packet.table_word) == [0x3f800000, 0xc1880000, 0x3f800000]
    assert list(packet.fifo_word[2:5]) == list(packet.table_word)
    assert packet.fifo_word[6] == 0x10000 - 0x4567
    existing[1] = 0xbf000000
    composed(3, existing, 0, 0, 0, 0x4567,
             ctypes.byref(plan), ctypes.byref(packet))
    assert list(packet.table_word) == [0x11111111, 0, 0x33333333]

    for name, start, preamble in (
        ("recovered_geometry_indexed_update_loop_97f20", 0x40,
         [5, 18, 0xc2700000, 0x4089999a, 0xc1a00000, 58]),
        ("recovered_geometry_indexed_update_loop_98000", 0x50,
         [5, 18, 0x42700000, 0x4089999a, 0xc1a00000, 58]),
        ("recovered_geometry_indexed_update_loop_98114", 0x60,
         [5, 18, 0xc1a00000, 0x4089999a, 0xc2700000, 58]),
        ("recovered_geometry_indexed_update_loop_98200", 0x70, []),
    ):
        loop_fn = getattr(ctypes.CDLL(str(library)), name)
        loop_fn.argtypes = [ctypes.POINTER(Loop)]
        loop = Loop(); loop_fn(ctypes.byref(loop))
        assert (loop.start_index, loop.end_exclusive, loop.iteration_count) == \
               (start, start + 0xf, 0xf)
        assert loop.packet_preamble_count == len(preamble)
        if preamble:
            assert list(loop.packet_preamble) == preamble
        assert (loop.update_target, loop.packet_target, loop.completion_word) == \
               (0x97d50, 0x97e10, 6)
        assert list(loop.window_word) == [0x403198, 0x403518, 0x84f888, 0]

    class ResponsePacket(ctypes.Structure):
        _fields_ = [("response_word", ctypes.c_uint32 * 3),
                    ("context_word", ctypes.c_uint32),
                    ("derived_word", ctypes.c_uint32),
                    ("fifo_word", ctypes.c_uint32 * 11),
                    ("fifo_count", ctypes.c_uint32)]
    post_fn = ctypes.CDLL(str(library)).recovered_geometry_indexed_post_loop_98200
    post_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.c_uint32, ctypes.POINTER(Post),
                        ctypes.POINTER(ResponsePacket)]
    post = Post(); response = ResponsePacket()
    post_fn(0x12345678, 0x2468, 0x11111111, 0x33333333,
            ctypes.byref(post), ctypes.byref(response))
    assert (post.source_byte, post.service_first, post.service_second,
            post.service_target) == (0x78, 0x7800, 0x6a00, 0x2a990)
    assert (post.completion_word, post.command29, post.command30,
            post.context_word, post.constant_word, post.zero_response_word,
            post.packet_target) == (6, 29, 30, 0x2468, 0x40b33333, 0, 0x982f8)
    assert list(response.response_word) == [0x11111111, 0, 0x33333333]
    assert list(response.fifo_word) == [18, 0x11111111, 0, 0x33333333,
                                        21, 0x10000 - 0x2468, 19,
                                        0x3f88f5c3, 0x3f800000, 0x3f800000, 58]
    listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
    handoff = listing[listing.index("   98268:"):listing.index("   982f8:")]
    for evidence in ("mov\t6,g9", "ldob\t0x5024e8,g0", "shlo\t8,g0,g0",
                     "call\t0x2a990", "mov\t29,g11", "0x40b33333",
                     "mov\t30,g8", "ld\t0x884000,g6"):
        if evidence not in handoff:
            raise AssertionError(f"98200 handoff listing evidence missing: {evidence}")
print("recovered geometry indexed table update 0x97d50: ok")
