#!/usr/bin/env python3
"""Host test for the recovered i960 per-object input consumer 0x24fc0.

Compiles von/i960/recovered_input_consumer_24fc0.c with
    cc -std=c11 -Wall -Wextra -Werror -shared -fPIC
and drives the pure helper against a locally allocated 0x600 object plus a
MAP_32BIT config blob (so object+0x6c holds a faithful 32-bit pointer).

The test covers the listing-verified behaviour:
  * 0x24f90-0x25038 reset, including the 0x24fc0/0x24fc4 object+0x136/+0x137
    seeds and the un-touched 0x13d/0x140/0x141 gap;
  * 0x2504c-0x2506c raw word capture into object+0xec/+0xf0;
  * 0x25118-0x2515c object+0x108 command decode from the 0x3d70/0x3da0 tables;
  * 0x26404-0x266a8 repeat/held/edge counter transitions;
  * 0x266a8-0x268c4 command -> object+0x136 action tree;
  * 0x268c4-0x26968 commit gate and object+0x137 latch.

object+0x1b2 is never written by these ranges; the test asserts it is
preserved and records the listing evidence that no store exists there.
"""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_input_consumer_24fc0.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

CC = ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC"]

OBJ_SIZE = 0x600
CFG_SIZE = 0x800
INPUT_BASE = 0xec
NO_CHANGE = None

PROT_READ = 0x1
PROT_WRITE = 0x2
MAP_PRIVATE = 0x2
MAP_ANONYMOUS = 0x20
MAP_32BIT = 0x40

# 0x3d70 / 0x3da0, identical 16-entry halfword tables.
NIBBLE = [0xff, 4, 0, 0xff, 6, 5, 7, 0xff,
          2, 3, 1, 0xff, 0xff, 0xff, 0xff, 0xff]


def low_buffer(size):
    """Anonymous MAP_32BIT mapping, so a pointer fits in object+0x6c's u32."""
    libc = ctypes.CDLL(None, use_errno=True)
    libc.mmap.restype = ctypes.c_void_p
    libc.mmap.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int,
                          ctypes.c_int, ctypes.c_int, ctypes.c_long]
    addr = libc.mmap(None, size, PROT_READ | PROT_WRITE,
                     MAP_PRIVATE | MAP_ANONYMOUS | MAP_32BIT, -1, 0)
    if not addr or addr == (1 << 64) - 1:
        raise OSError(ctypes.get_errno(), "mmap MAP_32BIT failed")
    return (ctypes.c_ubyte * size).from_address(addr)


def obj_u8(obj, offset):
    return obj[offset]


def set_obj_u8(obj, offset, value):
    obj[offset] = value & 0xff


def obj_u16(obj, offset):
    return ctypes.cast(ctypes.byref(obj, offset),
                       ctypes.POINTER(ctypes.c_uint16))[0]


def set_obj_u16(obj, offset, value):
    ctypes.cast(ctypes.byref(obj, offset),
                ctypes.POINTER(ctypes.c_uint16))[0] = value & 0xffff


def obj_u32(obj, offset):
    return ctypes.cast(ctypes.byref(obj, offset),
                       ctypes.POINTER(ctypes.c_uint32))[0]


def set_obj_u32(obj, offset, value):
    ctypes.cast(ctypes.byref(obj, offset),
                ctypes.POINTER(ctypes.c_uint32))[0] = value & 0xffffffff


def set_cfg_u32(cfg, offset, value):
    ctypes.cast(ctypes.byref(cfg, offset),
                ctypes.POINTER(ctypes.c_uint32))[0] = value & 0xffffffff


def command_arm_reference(code):
    """Independent tree decode of 0x266a8-0x268c4, literal-first branches."""
    if code > 0x504:
        if code > 0x706:
            if code == 0xff02:
                return 3
            if code > 0xff02:
                if code == 0xff05:
                    return 7
                if code > 0xff05:
                    if code == 0xff06:
                        return 6
                    if code == 0xff07:
                        return 5
                    return NO_CHANGE
                if code == 0xff03:
                    return 4
                if code == 0xff04:
                    return 1
                return NO_CHANGE
            if code == 0x7ff:
                return 5
            if code > 0x7ff:
                if code == 0xff00:
                    return 0
                if code == 0xff01:
                    return 2
                return NO_CHANGE
            if code == 0x707:
                return 5
            return NO_CHANGE
        if code > 0x704:
            return 6
        if code > 0x607:
            if code == 0x6ff:
                return 6
            if code < 0x6ff:
                return NO_CHANGE
            if code > 0x701:
                return NO_CHANGE
            return 0
        if code > 0x604:
            return 6
        if code > 0x507:
            if code == 0x5ff:
                return 7
            return NO_CHANGE
        if code > 0x505:
            return 6
        return 7
    if code > 0x502:
        return 1
    if code > 0x203:
        if code > 0x305:
            if code > 0x405:
                if code == 0x4ff:
                    return 1
                return NO_CHANGE
            if code > 0x402:
                return 1
            if code == 0x3ff:
                return 4
            return NO_CHANGE
        if code > 0x303:
            return 1
        if code > 0x302:
            return 4
        if code > 0x300:
            return 3
        if code == 0x2ff:
            return 3
        return NO_CHANGE
    if code > 0x200:
        return 3
    if code > 0x100:
        if code > 0x103:
            if code == 0x107:
                return 0
            if code == 0x1ff:
                return 2
            return NO_CHANGE
        if code > 0x101:
            return 3
        return 2
    if code > 0xfe:
        return 0
    if code <= 1:
        return 0
    if code == 7:
        return 0
    return NO_CHANGE


def command_from_word(word):
    return ((NIBBLE[(word >> 12) & 0x0f] << 8)
            | NIBBLE[(word >> 20) & 0x0f])


def word_for_command(hi_index, lo_index):
    return ((hi_index & 0x0f) << 12) | ((lo_index & 0x0f) << 20)


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "input-consumer.so"
        subprocess.run(CC + [str(SOURCE), "-o", str(library)], check=True)
        recovered = ctypes.CDLL(str(library))

        reset = recovered.recovered_input_consumer_24fc0_reset
        reset.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        reset.restype = None

        translate = recovered.recovered_input_consumer_24fc0_translate
        translate.argtypes = [ctypes.POINTER(ctypes.c_ubyte),
                              ctypes.c_uint32, ctypes.c_uint32]
        translate.restype = ctypes.c_uint32

        # The two required entry points must be exported. run() is the
        # absolute-global i960 wrapper and is intentionally not called here.
        assert recovered.recovered_input_consumer_24fc0_run

        class Ctx:
            def __init__(self):
                self.obj = (ctypes.c_ubyte * OBJ_SIZE)()
                self.cfg = low_buffer(CFG_SIZE)
                set_obj_u32(self.obj, 0x6c, ctypes.addressof(self.cfg))
                # object+0x30 == 0 selects the default nibble-table route.
                set_obj_u16(self.obj, 0x30, 0)
                set_cfg_u32(self.cfg, 0x60c, 7)

        # --- 0x24f90-0x25038 reset --------------------------------------
        ctx = Ctx()
        set_obj_u8(ctx.obj, 0x13d, 0xaa)   # gap byte, must survive
        set_obj_u8(ctx.obj, 0x140, 0xbb)
        set_obj_u8(ctx.obj, 0x141, 0xcc)
        set_obj_u8(ctx.obj, INPUT_BASE + 0x54, 0xdd)  # object+0x140
        set_obj_u8(ctx.obj, INPUT_BASE + 0x55, 0xee)  # object+0x141
        reset(ctx.obj)
        assert obj_u8(ctx.obj, 0x136) == 0xff          # 0x24fc0
        assert obj_u8(ctx.obj, 0x137) == 0xff          # 0x24fc4
        for off in (0x138, 0x139, 0x13a, 0x13b, 0x13c, 0x13e, 0x13f,
                    0x142, 0x143):
            assert obj_u8(ctx.obj, off) == 0, hex(off)
        # listing does not clear 0x13d/0x140/0x141
        assert obj_u8(ctx.obj, 0x13d) == 0xaa
        assert obj_u8(ctx.obj, INPUT_BASE + 0x54) == 0xdd
        assert obj_u8(ctx.obj, INPUT_BASE + 0x55) == 0xee
        assert obj_u16(ctx.obj, 0x102) == 0xffff
        assert obj_u16(ctx.obj, 0x104) == 0xffff
        assert obj_u16(ctx.obj, 0x106) == 0xffff
        assert obj_u16(ctx.obj, 0x108) == 0xffff
        assert obj_u32(ctx.obj, 0xec) == 0
        assert obj_u32(ctx.obj, 0xf0) == 0
        for i in range(8):
            assert obj_u16(ctx.obj, INPUT_BASE + 0x28 + i * 2) == 0
            assert obj_u16(ctx.obj, INPUT_BASE + 0x38 + i * 2) == 0

        # --- 0x2504c-0x2506c raw word capture ---------------------------
        ctx = Ctx()
        set_obj_u8(ctx.obj, 0x136, 0xab)
        code = translate(ctx.obj, 0xdeadbeef, 0x12345678)
        assert obj_u32(ctx.obj, 0xec) == 0xdeadbeef
        assert obj_u32(ctx.obj, 0xf0) == 0x12345678
        # object+0x108 was zero before the call, so the shadow keeps 0.
        assert obj_u16(ctx.obj, 0x106) == 0
        assert obj_u16(ctx.obj, 0x108) == code
        assert code == command_from_word(0xdeadbeef), hex(code)

        # --- 0x25118-0x2515c command decode + 0x266a8 action tree --------
        for hi_index, lo_index in ((0, 0), (8, 10), (6, 2), (0, 1),
                                   (5, 4), (10, 8)):
            ma = word_for_command(hi_index, lo_index)
            cmd = command_from_word(ma)
            case = Ctx()
            set_obj_u8(case.obj, INPUT_BASE + 0x4a, 0xab)
            got = translate(case.obj, ma, 0)
            assert got == cmd, (hex(ma), hex(got), hex(cmd))
            ref = command_arm_reference(cmd)
            if ref is NO_CHANGE:
                assert obj_u8(case.obj, INPUT_BASE + 0x4a) == 0xab, hex(cmd)
                assert obj_u8(case.obj, 0x136) == 0xab, hex(cmd)
            else:
                assert obj_u8(case.obj, INPUT_BASE + 0x4a) == ref, \
                    (hex(cmd), ref)
                assert obj_u8(case.obj, 0x136) == ref, (hex(cmd), ref)

        # explicit command-arm spot check against the listing
        explicit = {
            0xff00: 0, 0xff01: 2, 0xff02: 3, 0xff03: 4, 0xff04: 1,
            0xff05: 7, 0xff06: 6, 0xff07: 5, 0x0505: 7, 0x0506: 6,
            0x0507: 6, 0x0700: 0, 0x0701: 0, 0x0704: NO_CHANGE,
            0x0705: 6, 0x0706: 6, 0x0707: 5,
            0x0101: 2, 0x0102: 3, 0x0107: 0, 0x01ff: 2, 0x0201: 3,
        }
        for code, value in explicit.items():
            assert command_arm_reference(code) == value, hex(code)

        # --- 0x25040 head gated stores -----------------------------------
        # command == 0x0602 (0x25314): object+0x136 = 0xff, object+0x50 = 0
        case = Ctx()
        set_obj_u16(case.obj, 0x108, 0x0602)  # pre-existing command
        ma_602 = word_for_command(4, 8)       # table[4]=6, table[8]=2 -> 0x0602
        assert command_from_word(ma_602) == 0x0602
        set_obj_u8(case.obj, INPUT_BASE + 0x4f, 0)
        set_obj_u8(case.obj, INPUT_BASE + 0x4a, 0x11)
        translate(case.obj, ma_602, 0)
        assert obj_u8(case.obj, 0x136) == 0xff
        assert obj_u8(case.obj, INPUT_BASE + 0x4f) == 0xff  # 0 -> 0xff
        assert obj_u8(case.obj, INPUT_BASE + 0x50) == 0
        # object+0x4f = 5 decrements
        case = Ctx()
        set_obj_u8(case.obj, INPUT_BASE + 0x4f, 5)
        translate(case.obj, ma_602, 0)
        assert obj_u8(case.obj, INPUT_BASE + 0x4f) == 4

        # command == 0x0206 (0x2525c): object+0x50 repeat + object+0x102 clear
        case = Ctx()
        ma_206 = word_for_command(8, 4)       # table[8]=2, table[4]=6 -> 0x0206
        assert command_from_word(ma_206) == 0x0206
        set_obj_u16(case.obj, INPUT_BASE + 0x16, 0xabcd)
        set_obj_u8(case.obj, INPUT_BASE + 0x50, 0)
        set_obj_u8(case.obj, INPUT_BASE + 0x4a, 0x22)
        translate(case.obj, ma_206, 0)
        assert obj_u8(case.obj, 0x136) == 0xff
        assert obj_u8(case.obj, INPUT_BASE + 0x50) == 0xff
        assert obj_u16(case.obj, INPUT_BASE + 0x16) == 0
        # default route: command 0xffff -> object+0x4f/0x50 cleared
        case = Ctx()
        set_obj_u8(case.obj, INPUT_BASE + 0x4f, 7)
        set_obj_u8(case.obj, INPUT_BASE + 0x50, 9)
        translate(case.obj, 0, 0)
        assert obj_u8(case.obj, INPUT_BASE + 0x4f) == 0
        assert obj_u8(case.obj, INPUT_BASE + 0x50) == 0

        # object+0x30 == 6 (0x250f4-0x25114): command 0xffff and words cleared
        case = Ctx()
        set_obj_u16(case.obj, 0x30, 6)
        set_obj_u32(case.obj, 0xec, 0x11111111)
        set_obj_u32(case.obj, 0xf0, 0x22222222)
        set_obj_u8(case.obj, INPUT_BASE + 0x4a, 0x33)
        translate(case.obj, 0x804000, 0)
        assert obj_u16(case.obj, 0x108) == 0xffff
        assert obj_u32(case.obj, 0xec) == 0
        assert obj_u32(case.obj, 0xf0) == 0
        assert obj_u8(case.obj, 0x136) == 0x33  # command 0xffff -> no store

        # --- 0x26404-0x266a8 repeat/held/edge counters -------------------
        def counter_case(ma, mb, initial, expected):
            case = Ctx()
            for off in (0x4c, 0x4d, 0x4e, 0x52, 0x53, 0x54, 0x55,
                        0x56, 0x57):
                set_obj_u8(case.obj, INPUT_BASE + off, initial)
            translate(case.obj, ma, mb)
            got = {off: obj_u8(case.obj, INPUT_BASE + off)
                   for off in expected}
            assert got == expected, (hex(ma), hex(mb), got, expected)

        # all counters start at 5; the *_HI / *_LO clears dominate
        counter_case(0x00010000, 0x00000000, 5,
                     {0x4c: 0xff, 0x4d: 0x00, 0x4e: 0x00, 0x52: 0x00,
                      0x53: 0x00, 0x54: 5, 0x55: 5, 0x56: 0x00, 0x57: 0x00})
        counter_case(0x00000000, 0x00010000, 5,
                     {0x4c: 0x04, 0x4d: 0x00, 0x4e: 0x00, 0x52: 0x00,
                      0x53: 0xff, 0x54: 5, 0x55: 6, 0x56: 0x00, 0x57: 0x00})
        counter_case(0x00000000, 0x00000100, 5,
                     {0x4c: 0x00, 0x4d: 0x04, 0x4e: 0x00, 0x52: 0xff,
                      0x53: 0x00, 0x54: 6, 0x55: 5, 0x56: 0x00, 0x57: 0x00})
        counter_case(0x00000100, 0x00000000, 5,
                     {0x4c: 0x00, 0x4d: 0xff, 0x4e: 0x04, 0x52: 0x00,
                      0x53: 0x00, 0x54: 5, 0x55: 5, 0x56: 0x00, 0x57: 0x00})
        counter_case(0x00000000, 0x00000200, 5,
                     {0x4c: 0x00, 0x4d: 0x00, 0x4e: 0x00, 0x52: 0x00,
                      0x53: 0x00, 0x54: 5, 0x55: 5, 0x56: 0xff, 0x57: 0x00})
        counter_case(0x00000000, 0x00020000, 5,
                     {0x4c: 0x00, 0x4d: 0x00, 0x4e: 0x00, 0x52: 0x00,
                      0x53: 0x00, 0x54: 5, 0x55: 5, 0x56: 0x00, 0x57: 0xff})

        # 0xfb chord: keep 0x52/0x53 from being cleared by the ma clears
        case = Ctx()
        for off, value in ((0x4c, 0xfd), (0x4d, 0xfd), (0x4e, 0x00),
                           (0x52, 0xfd), (0x53, 0xfd), (0x54, 0),
                           (0x55, 0), (0x56, 0), (0x57, 0)):
            set_obj_u8(case.obj, INPUT_BASE + off, value)
        translate(case.obj, 0x00010100, 0)   # bits 16 and 8 set, no clears
        assert obj_u8(case.obj, INPUT_BASE + 0x52) == 0
        assert obj_u8(case.obj, INPUT_BASE + 0x53) == 0
        assert obj_u8(case.obj, INPUT_BASE + 0x4e) == 0xff
        assert obj_u8(case.obj, INPUT_BASE + 0x4c) == 0xfc
        assert obj_u8(case.obj, INPUT_BASE + 0x4d) == 0xfc

        # 0xfd reset window: 0xfd is reset via 0x4c = 0xff, 0xff is not
        case = Ctx()
        set_obj_u8(case.obj, INPUT_BASE + 0x53, 0xfd)
        translate(case.obj, 0x00010100, 0)
        assert obj_u8(case.obj, INPUT_BASE + 0x53) == 0
        assert obj_u8(case.obj, INPUT_BASE + 0x4c) == 0xff
        case = Ctx()
        set_obj_u8(case.obj, INPUT_BASE + 0x53, 0xff)
        translate(case.obj, 0x00010100, 0)
        assert obj_u8(case.obj, INPUT_BASE + 0x53) == 0xfe

        # --- 0x268c4-0x26968 commit gate and latch ------------------------
        def gate_case(mb, old_command, state, action, timer=100, advance=7):
            case = Ctx()
            set_cfg_u32(case.cfg, 0x60c, advance)
            set_obj_u16(case.obj, 0x1f0, timer)
            # 0x25070-0x25080 copies object+0x108 into object+0x106, which is
            # exactly what the 0x268e8 gate reads.
            set_obj_u16(case.obj, 0x108, old_command)
            set_obj_u16(case.obj, 0x172, state)
            set_obj_u8(case.obj, INPUT_BASE + 0x4a, action)
            set_obj_u8(case.obj, INPUT_BASE + 0x4b, 0x5a)
            # ma=0 yields command 0xffff (no tree store); mb bit17 sets 0x57,
            # mb bit9 sets 0x56.
            translate(case.obj, 0, mb)
            return case

        # gate A: 0x57 -> 0xff (mb bit17) and object+0x106 == 0xffff
        g = gate_case(0x00020000, 0xffff, 0x0000, 5)
        assert obj_u8(g.obj, 0x137) == 5
        assert obj_u16(g.obj, 0x1f0) == 107
        # gate A also trips through 0x56 (mb bit9)
        g = gate_case(0x00000200, 0xffff, 0x0000, 5)
        assert obj_u8(g.obj, 0x137) == 5
        # gate A false when object+0x106 != 0xffff and state not listed
        g = gate_case(0x00020000, 0x0000, 17, 5)
        assert obj_u8(g.obj, 0x137) == 0x5a
        assert obj_u16(g.obj, 0x1f0) == 100
        # gate B: 0x57 > 0xf5 with state 15/16/31
        for state in (15, 16, 31):
            g = gate_case(0x00020000, 0x0000, state, 6)
            assert obj_u8(g.obj, 0x137) == 6, state
        # latch value 0xff suppresses the timer advance
        g = gate_case(0x00020000, 0xffff, 0x0000, 0xff)
        assert obj_u8(g.obj, 0x137) == 0xff
        assert obj_u16(g.obj, 0x1f0) == 100

        # --- object+0x1b2 is outside this unit ---------------------------
        case = Ctx()
        set_obj_u16(case.obj, 0x1b2, 0x1234)
        translate(case.obj, 0x804000, 0)
        assert obj_u16(case.obj, 0x1b2) == 0x1234

        # --- listing evidence -------------------------------------------
        listing = LISTING.read_text(encoding="utf-8")
        head = listing[listing.index("   24f80:"):listing.index("   25364:")]
        tail = listing[listing.index("   26340:"):listing.index("   266a8:")]
        tree = listing[listing.index("   266a8:"):listing.index("   26980:")]
        for evidence in (
                "stob\tg4,0x136(g0)", "stob\tg4,0x137(g0)",
                "ld\t0x50249c,g4", "ld\t0x5024a4,g4",
                "st\tg4,(r14)", "st\tg4,0xf0(g0)",
                "ldos\t0x108(g0),g4", "stos\tg4,0x106(g0)",
                "ld\t0x3d90,g5", "ld\t0x3dc0,g6",
                "ldos\t0x3d70[g4*2],g5", "ldos\t0x3da0[g4*2],g4",
                "stos\tg5,0x108(g0)",
                "stob\tr14,0x4a(r15)", "stob\tg14,0x4f(r15)"):
            if evidence not in head:
                raise AssertionError(f"consumer head evidence missing: "
                                     f"{evidence}")
        for evidence in (
                "call\t0x72ea0",
                "stob\tg14,0x4d(r15)", "stob\tg14,0x4e(r14)",
                "ld\t0x3d98,g5", "ld\t0x3dc8,g5"):
            if evidence not in tail:
                raise AssertionError(f"consumer counter evidence missing: "
                                     f"{evidence}")
        for evidence in (
                "stob\tr15,0x4a(r14)", "stob\tg14,0x4a(r14)",
                "stob\tg4,0x4b(r14)", "ldob\t0x4a(r14),g4"):
            if evidence not in tree:
                raise AssertionError(f"consumer tree/latch evidence missing: "
                                     f"{evidence}")
        if "0x1b2" in head or "0x1b2" in tail or "0x1b2" in tree:
            raise AssertionError("0x1b2 must not be written in the unit ranges")
        # the entire sibling body, including the uncited middle, is clean too
        sibling = listing[listing.index("   25040:"):listing.index("   26980:")]
        if "0x1b2" in sibling:
            raise AssertionError("0x1b2 written inside the 0x25040 sibling body")

    print("PASS: 0x24fc0-0x25360 recovered input consumer / action translation")


if __name__ == "__main__":
    main()
