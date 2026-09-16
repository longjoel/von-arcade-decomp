#!/usr/bin/env python3
"""Host test for the recovered i960 gameplay input-commit body 0x72ea0-0x73480.

Compiles von/i960/recovered_input_commit_run_72ea0.c with
    cc -std=c11 -Wall -Wextra -Werror -shared -fPIC
and drives the pure core against a locally allocated 0x600 object plus
writable copies of the globals. The config pointer stored in object+0x6c is
placed in a MAP_32BIT mapping so the core's 32-bit pointer load is faithful.
"""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_input_commit_run_72ea0.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

CC = ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC"]

OBJ_SIZE = 0x600
REC_STRIDE = 0x700
REC_BYTES = 2 * REC_STRIDE + 0x600
CFG_SIZE = 0x800
NO_CHANGE = None  # command arm that leaves g7+0x4a untouched

PROT_READ = 0x1
PROT_WRITE = 0x2
MAP_PRIVATE = 0x2
MAP_ANONYMOUS = 0x20
MAP_32BIT = 0x40


def low_buffer(size):
    """Anonymous MAP_32BIT mapping, so a pointer fits in the core's u32 slot."""
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


def set_cfg_u32(cfg, offset, value):
    ctypes.cast(ctypes.byref(cfg, offset),
                ctypes.POINTER(ctypes.c_uint32))[0] = value & 0xffffffff


def command_arm_reference(code):
    """Independent tree decode of 0x7320c-0x733f0, literal-first branches."""
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


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "input-commit.so"
        subprocess.run(CC + [str(SOURCE), "-o", str(library)], check=True)
        recovered = ctypes.CDLL(str(library))
        core = recovered.recovered_input_commit_run_72ea0_core
        core.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_ubyte),
        ]
        core.restype = None

        class Ctx:
            def __init__(self):
                self.obj = (ctypes.c_ubyte * OBJ_SIZE)()
                self.ma = ctypes.c_uint32(0)
                self.mb = ctypes.c_uint32(0)
                self.cfg = low_buffer(CFG_SIZE)
                self.rec = (ctypes.c_ubyte * REC_BYTES)()
                obj_u32 = ctypes.cast(self.obj,
                                      ctypes.POINTER(ctypes.c_uint32))
                obj_u32[0x6c // 4] = ctypes.addressof(self.cfg)
                set_obj_u16(self.obj, 0x108, 3)  # command arm: no change
                set_cfg_u32(self.cfg, 0x610, 1000)
                set_cfg_u32(self.cfg, 0x60c, 250)

        def run(ctx, mode=0, state=0, game=0, port_bit=0):
            core(ctx.obj, ctypes.byref(ctx.ma), ctypes.byref(ctx.mb),
                 mode, state, game, port_bit, ctx.rec)

        # --- Phase A: 0x72ea0-0x72f04 -----------------------------------
        ctx = Ctx()
        ctx.rec[0x514] = 0x80
        ctx.rec[0x515] = 0x7f
        ctx.rec[REC_STRIDE + 0x514] = 0x7e
        ctx.rec[REC_STRIDE + 0x515] = 0x02
        run(ctx, mode=2, state=4, port_bit=0)
        assert ctx.ma.value == 0xffffff80, hex(ctx.ma.value)
        assert ctx.mb.value == 0x7f, hex(ctx.mb.value)
        run(ctx, mode=2, state=4, port_bit=1)
        assert ctx.ma.value == 0x7e, hex(ctx.ma.value)
        assert ctx.mb.value == 0x02, hex(ctx.mb.value)
        run(ctx, mode=2, state=4, port_bit=3)  # only bit 0 selects
        assert (ctx.ma.value, ctx.mb.value) == (0x7e, 0x02)
        run(ctx, mode=2, state=5, port_bit=0)  # state gate
        assert (ctx.ma.value, ctx.mb.value) == (0x7e, 0x02)
        run(ctx, mode=3, state=4, port_bit=1)  # mode gate
        assert (ctx.ma.value, ctx.mb.value) == (0x7e, 0x02)

        # game==12 override (0x72f50-0x72f64)
        ctx = Ctx()
        ctx.ma.value = 0x40
        ctx.mb.value = 0x50
        run(ctx, game=12)
        assert (ctx.ma.value, ctx.mb.value) == (1, 1)

        # --- Phase B: 0x72f68-0x7300c -----------------------------------
        ctx = Ctx()
        set_obj_u16(ctx.obj, 0x1f0, 500)          # cap 1000, advance 250
        run(ctx)
        assert obj_u16(ctx.obj, 0x1f0) == 499
        assert obj_u16(ctx.obj, 0x1e0) == 1       # 499 <= 750
        assert obj_u16(ctx.obj, 0x1e8) == 50      # 100*501/1000
        ctx = Ctx()
        set_obj_u16(ctx.obj, 0x1f0, 2000)
        run(ctx)
        assert obj_u16(ctx.obj, 0x1f0) == 1000    # clamped to cap
        assert obj_u16(ctx.obj, 0x1e0) == 0       # 1000 > 750
        assert obj_u16(ctx.obj, 0x1e8) == 0
        ctx = Ctx()
        set_obj_u16(ctx.obj, 0x1f0, 1)
        run(ctx)
        assert obj_u16(ctx.obj, 0x1f0) == 0
        assert obj_u16(ctx.obj, 0x1e0) == 1
        assert obj_u16(ctx.obj, 0x1e8) == 100
        ctx = Ctx()
        set_obj_u16(ctx.obj, 0x1f0, 0x8000)       # signed negative: no decrement
        run(ctx)
        assert obj_u16(ctx.obj, 0x1f0) == 1000
        ctx = Ctx()
        set_obj_u16(ctx.obj, 0x1f0, 0)
        run(ctx)
        assert obj_u16(ctx.obj, 0x1f0) == 0
        assert obj_u16(ctx.obj, 0x1e0) == 1
        assert obj_u16(ctx.obj, 0x1e8) == 100

        # --- Phase C: 0x73010-0x7320c, one input bit at a time ----------
        def counter_case(p_a, p_b, expected):
            case = Ctx()
            for offset in (0x4c, 0x4d, 0x4e, 0x52, 0x53, 0x54, 0x55,
                           0x56, 0x57):
                set_obj_u8(case.obj, 0xec + offset, 5)
            case.ma.value = p_a
            case.mb.value = p_b
            run(case)
            got = {off: obj_u8(case.obj, 0xec + off) for off in expected}
            assert got == expected, (hex(p_a), hex(p_b), got, expected)

        p_a_cases = {
            0x01: {0x4c: 0, 0x4d: 0, 0x4e: 0, 0x52: 0, 0x53: 0, 0x54: 5,
                   0x55: 5, 0x56: 0, 0x57: 0},
            0x02: {0x4c: 0, 0x4d: 4, 0x4e: 0, 0x52: 0xff, 0x53: 0, 0x54: 6,
                   0x55: 5, 0x56: 0, 0x57: 0},
            0x04: {0x4c: 0, 0x4d: 0xff, 0x4e: 4, 0x52: 0, 0x53: 0, 0x54: 5,
                   0x55: 5, 0x56: 0, 0x57: 0},
            0x10: {0x4c: 0, 0x4d: 0, 0x4e: 0, 0x52: 0, 0x53: 0, 0x54: 5,
                   0x55: 5, 0x56: 0xff, 0x57: 0},
            0x20: {0x4c: 0, 0x4d: 0, 0x4e: 0, 0x52: 0, 0x53: 0, 0x54: 5,
                   0x55: 5, 0x56: 4, 0x57: 0},
        }
        for p_a, expected in p_a_cases.items():
            counter_case(p_a, 0x00, expected)

        p_b_cases = {
            0x01: {0x4c: 0, 0x4d: 0, 0x4e: 0, 0x52: 0, 0x53: 0, 0x54: 5,
                   0x55: 5, 0x56: 0, 0x57: 0},
            0x02: {0x4c: 4, 0x4d: 0, 0x4e: 0, 0x52: 0, 0x53: 0xff, 0x54: 5,
                   0x55: 6, 0x56: 0, 0x57: 0},
            0x04: {0x4c: 0xff, 0x4d: 0, 0x4e: 0, 0x52: 0, 0x53: 0, 0x54: 5,
                   0x55: 5, 0x56: 0, 0x57: 0},
            0x10: {0x4c: 0, 0x4d: 0, 0x4e: 0, 0x52: 0, 0x53: 0, 0x54: 5,
                   0x55: 5, 0x56: 0, 0x57: 0xff},
            0x20: {0x4c: 0, 0x4d: 0, 0x4e: 0, 0x52: 0, 0x53: 0, 0x54: 5,
                   0x55: 5, 0x56: 0, 0x57: 4},
        }
        for p_b, expected in p_b_cases.items():
            counter_case(0x00, p_b, expected)

        # chord rule: both > 0xfb -> X52 = X53 = 0, E = 0xff
        chord = Ctx()
        set_obj_u8(chord.obj, 0xec + 0x52, 0xfd)
        set_obj_u8(chord.obj, 0xec + 0x53, 0xfd)
        chord.ma.value = 0x02
        chord.mb.value = 0x02
        run(chord)
        assert obj_u8(chord.obj, 0xec + 0x52) == 0
        assert obj_u8(chord.obj, 0xec + 0x53) == 0
        assert obj_u8(chord.obj, 0xec + 0x4e) == 0xff

        # 0xfd reset window: 0xff survives, 0xfd is reset via 0x4c = 0xff.
        fd = Ctx()
        set_obj_u8(fd.obj, 0xec + 0x53, 0xfd)
        fd.mb.value = 0x04
        run(fd)
        assert obj_u8(fd.obj, 0xec + 0x53) == 0
        assert obj_u8(fd.obj, 0xec + 0x4c) == 0xff
        fd = Ctx()
        set_obj_u8(fd.obj, 0xec + 0x53, 0xff)
        fd.mb.value = 0x04
        run(fd)
        assert obj_u8(fd.obj, 0xec + 0x53) == 0xfe  # > 0xfd is not reset

        # --- Phase D: every command code --------------------------------
        cmd = Ctx()
        for code in range(0x10000):
            set_obj_u8(cmd.obj, 0xec + 0x4a, 0xab)
            set_obj_u16(cmd.obj, 0x108, code)
            run(cmd)
            expected = command_arm_reference(code)
            if expected is NO_CHANGE:
                assert obj_u8(cmd.obj, 0xec + 0x4a) == 0xab, hex(code)
            else:
                assert obj_u8(cmd.obj, 0xec + 0x4a) == expected, hex(code)

        explicit = {
            0x000: 0, 0x001: 0, 0x007: 0, 0x0ff: 0, 0x100: 0,
            0x101: 2, 0x102: 3, 0x103: 3, 0x107: 0, 0x1ff: 2,
            0x201: 3, 0x202: 3, 0x203: 3, 0x2ff: 3, 0x301: 3, 0x302: 3,
            0x303: 4, 0x304: 1, 0x305: 1, 0x3ff: 4, 0x403: 1, 0x404: 1,
            0x405: 1, 0x4ff: 1, 0x503: 1, 0x504: 1, 0x505: 7, 0x506: 6,
            0x507: 6, 0x5ff: 7, 0x605: 6, 0x606: 6, 0x607: 6, 0x6ff: 6,
            0x700: 0, 0x701: 0, 0x707: 5, 0x7ff: 5, 0xff00: 0, 0xff01: 2,
            0xff02: 3, 0xff03: 4, 0xff04: 1, 0xff05: 7, 0xff06: 6,
            0xff07: 5,
        }
        for code, value in explicit.items():
            assert command_arm_reference(code) == value, hex(code)

        # --- Phase E: commit gate, latch, and timer advance -------------
        def gate_case(p_a, p_b, pre_56, pre_57, target_106, state,
                      code=3, action=6, timer=0, advance=250, cap=1000):
            case = Ctx()
            set_cfg_u32(case.cfg, 0x610, cap)
            set_cfg_u32(case.cfg, 0x60c, advance)
            set_obj_u16(case.obj, 0x1f0, timer)
            set_obj_u16(case.obj, 0x106, target_106)
            set_obj_u16(case.obj, 0x172, state)
            set_obj_u8(case.obj, 0xec + 0x56, pre_56)
            set_obj_u8(case.obj, 0xec + 0x57, pre_57)
            set_obj_u8(case.obj, 0xec + 0x4a, action)
            set_obj_u16(case.obj, 0x108, code)
            case.ma.value = p_a
            case.mb.value = p_b
            run(case)
            return case

        # gate A: S57 > 0xee (0xf0 -> 0xef via bit5) and +0x106 == 0xffff
        g = gate_case(0x00, 0x20, 0x00, 0xf0, 0xffff, 0x0000)
        assert obj_u8(g.obj, 0xec + 0x4b) == 6
        assert obj_u16(g.obj, 0x1f0) == 250
        # boundary: 0xee does not trip gate A
        g = gate_case(0x00, 0x20, 0x00, 0xef, 0xffff, 0x0000)
        assert obj_u8(g.obj, 0xec + 0x4b) == 0
        assert obj_u16(g.obj, 0x1f0) == 0
        # S56 path and latch value 0xff suppresses the advance
        g = gate_case(0x10, 0x00, 0x00, 0x00, 0xffff, 0x0000, action=0xff)
        assert obj_u8(g.obj, 0xec + 0x4b) == 0xff
        assert obj_u16(g.obj, 0x1f0) == 0
        # gate B: S57 > 0xf5 (0xf7 -> 0xf6) with state 15
        g = gate_case(0x00, 0x20, 0x00, 0xf7, 0x0000, 15, action=5)
        assert obj_u8(g.obj, 0xec + 0x4b) == 5
        assert obj_u16(g.obj, 0x1f0) == 250
        assert gate_case(0x00, 0x20, 0x00, 0xf7, 0x0000, 16, action=5) \
            .obj[0xec + 0x4b] == 5
        assert gate_case(0x00, 0x20, 0x00, 0xf7, 0x0000, 31, action=5) \
            .obj[0xec + 0x4b] == 5
        # gate B rejects an unlisted state and the 0xf5 boundary
        g = gate_case(0x00, 0x20, 0x00, 0xf7, 0x0000, 17, action=5)
        assert obj_u8(g.obj, 0xec + 0x4b) == 0
        g = gate_case(0x00, 0x20, 0x00, 0xf6, 0x0000, 15, action=5)
        assert obj_u8(g.obj, 0xec + 0x4b) == 0
        # gate A false with both counters at 0xee, even with state 15
        g = gate_case(0x20, 0x20, 0xef, 0xef, 0xffff, 15, action=5)
        assert obj_u8(g.obj, 0xec + 0x56) == 0xee
        assert obj_u8(g.obj, 0xec + 0x57) == 0xee
        assert obj_u8(g.obj, 0xec + 0x4b) == 0
        assert obj_u16(g.obj, 0x1f0) == 0

        # --- listing evidence, 0x72ea0-0x73480 --------------------------
        listing = LISTING.read_text(encoding="utf-8")
        start = listing.index("   72ea0:")
        end = listing.index("\n   73490:", start)
        block = listing[start:end]
        for evidence in (
                "stob\tg4,0x138", "stob\tg14,0x4e", "stob\tg14,0x4d",
                "stob\tg14,0x4a", "stob\tg14,0x52", "stob\tg14,0x53",
                "lda\t0xfb,", "lda\t0xfd,", "lda\t0xee,", "lda\t0xf5,",
                "cmpibne\t4,g4,0x72f08", "cmpibne\t12,g4,0x72f68",
                "addo\tg4,g5,g4", "stos\tg4,0x1f0(r4)"):
            if evidence not in block:
                raise AssertionError(f"input-commit listing evidence missing: "
                                     f"{evidence}")
        # the 0x26340 producer call is a separate call site
        if "call\t0x72ea0" not in listing:
            raise AssertionError("producer call 0x72ea0 missing from listing")
        if "call\t0x72ea0" in block:
            raise AssertionError("producer call must not be inside the body")

    print("PASS: 0x72ea0-0x73480 recovered input-commit")


if __name__ == "__main__":
    main()
