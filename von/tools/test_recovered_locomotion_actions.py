#!/usr/bin/env python3
"""Validate the recovered i960 locomotion action arms 0 and 12.

Compiles von/i960/recovered_locomotion_actions.c with
    cc -std=c11 -Wall -Wextra -Werror -shared -fPIC
and drives the pure cores against a locally allocated 0x600 object plus a
config block.  The config pointer stored at object+0x6c is placed in a
MAP_32BIT mapping so the core's 32-bit pointer load is faithful.

Listing spans:
    arm 0  0x000329c4-0x00032a88   auto-face slew (+0x2e), +0x10a advance,
                                    g3+0x1a mode-target turn via cfg+0x528
    arm 12 0x00032ea4-0x00032fd0   opcode-10 response snap (+0x2e) via
                                    cfg+0x52c, +0x1c4 rescale, +0x184 latch,
                                    +0x1b2 clear

The opcode-10 projection is the 0x6f6f0 family; the bounded model consumes
the response the 0x32810 prefix caches at object+0x84.
"""

import ctypes
import pathlib
import struct
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_locomotion_actions.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

CC = ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC"]

OBJ_SIZE = 0x600
CFG_SIZE = 0x800
STATE_SIZE = 0x200
STATE_STRIDE = 0x10

PROT_READ = 0x1
PROT_WRITE = 0x2
MAP_PRIVATE = 0x2
MAP_ANONYMOUS = 0x20
MAP_32BIT = 0x40


def bits(value):
    return struct.unpack("<I", struct.pack("<f", value))[0]


def float_of(word):
    return struct.unpack("<f", struct.pack("<I", word))[0]


def low_buffer(size):
    """Anonymous MAP_32BIT mapping, so a pointer fits in the u32 slot."""
    libc = ctypes.CDLL(None, use_errno=True)
    libc.mmap.restype = ctypes.c_void_p
    libc.mmap.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int,
                          ctypes.c_int, ctypes.c_int, ctypes.c_long]
    addr = libc.mmap(None, size, PROT_READ | PROT_WRITE,
                     MAP_PRIVATE | MAP_ANONYMOUS | MAP_32BIT, -1, 0)
    if not addr or addr == (1 << 64) - 1:
        raise OSError(ctypes.get_errno(), "mmap MAP_32BIT failed")
    return (ctypes.c_ubyte * size).from_address(addr)


def obj_u16(obj, offset):
    return ctypes.cast(ctypes.byref(obj, offset),
                       ctypes.POINTER(ctypes.c_uint16))[0]


def set_obj_u16(obj, offset, value):
    ctypes.cast(ctypes.byref(obj, offset),
                ctypes.POINTER(ctypes.c_uint16))[0] = value & 0xffff


def set_obj_u32(obj, offset, value):
    ctypes.cast(ctypes.byref(obj, offset),
                ctypes.POINTER(ctypes.c_uint32))[0] = value & 0xffffffff


def set_cfg_u32(cfg, offset, value):
    ctypes.cast(ctypes.byref(cfg, offset),
                ctypes.POINTER(ctypes.c_uint32))[0] = value & 0xffffffff


def set_state_gate(state, index, value):
    ctypes.cast(ctypes.byref(state, index * STATE_STRIDE),
                ctypes.POINTER(ctypes.c_uint32))[0] = value & 0xffffffff


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "locomotion-actions.so"
        subprocess.run(CC + [str(SOURCE), "-o", str(library)], check=True)
        recovered = ctypes.CDLL(str(library))

        arm0 = recovered.recovered_locomotion_action_0_core
        arm0.argtypes = [ctypes.POINTER(ctypes.c_ubyte),
                         ctypes.POINTER(ctypes.c_ubyte),
                         ctypes.POINTER(ctypes.c_uint16)]
        arm0.restype = None

        arm0_run = recovered.recovered_locomotion_action_0_run
        arm0_run.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        arm0_run.restype = None

        arm12 = recovered.recovered_locomotion_action_12_core
        arm12.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        arm12.restype = None

        arm12_run = recovered.recovered_locomotion_action_12_run
        arm12_run.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        arm12_run.restype = None

        class Ctx:
            def __init__(self):
                self.obj = (ctypes.c_ubyte * OBJ_SIZE)()
                self.cfg = low_buffer(CFG_SIZE)
                self.state = (ctypes.c_ubyte * STATE_SIZE)()
                self.mode = ctypes.c_uint16(0)
                obj_u32 = ctypes.cast(self.obj,
                                      ctypes.POINTER(ctypes.c_uint32))
                obj_u32[0x6c // 4] = ctypes.addressof(self.cfg)

        # --- arm 0: auto-face gate set, saturated slew -----------------------
        # target = +0x184 + +0x34 = 0x1000 + 0x100 = 0x1100
        # delta = 0x1100 - 0x800 = 0x900 -> clamped to +0x300
        # +0x2e = 0x800 + 0x300 + 0x10a = 0xB20, +0x184 = 0x1000 + 0x10a
        ctx = Ctx()
        set_cfg_u32(ctx.cfg, 0x528, 0x1000)
        set_obj_u16(ctx.obj, 0x172, 1)
        set_state_gate(ctx.state, 1, 1)
        set_obj_u16(ctx.obj, 0x184, 0x1000)
        set_obj_u16(ctx.obj, 0x34, 0x100)
        set_obj_u16(ctx.obj, 0x2e, 0x800)
        set_obj_u16(ctx.obj, 0x10a, 0x20)
        ctx.mode.value = 0x100
        arm0(ctx.obj, ctx.state, ctypes.byref(ctx.mode))
        assert obj_u16(ctx.obj, 0x2e) == 0xB20, hex(obj_u16(ctx.obj, 0x2e))
        assert obj_u16(ctx.obj, 0x184) == 0x1020, hex(obj_u16(ctx.obj, 0x184))
        # mode target 0x100 -> +0x184 within +/-cfg+0x528 -> lands on +0x184
        assert ctx.mode.value == 0x1020, hex(ctx.mode.value)

        # --- arm 0: negative saturated slew ----------------------------------
        ctx = Ctx()
        set_cfg_u32(ctx.cfg, 0x528, 0x40)
        set_obj_u16(ctx.obj, 0x172, 1)
        set_state_gate(ctx.state, 1, 1)
        set_obj_u16(ctx.obj, 0x184, 0x100)
        set_obj_u16(ctx.obj, 0x34, 0x000)
        set_obj_u16(ctx.obj, 0x2e, 0x500)
        set_obj_u16(ctx.obj, 0x10a, 2)
        ctx.mode.value = 0x20
        arm0(ctx.obj, ctx.state, ctypes.byref(ctx.mode))
        # delta = 0x100 - 0x500 = -0x400 -> -0x300; +0x2e = 0x202
        assert obj_u16(ctx.obj, 0x2e) == 0x202, hex(obj_u16(ctx.obj, 0x2e))
        assert obj_u16(ctx.obj, 0x184) == 0x102
        # mode delta = 0x102 - 0x20 = 0xE2 > 0x40 -> +0x40
        assert ctx.mode.value == 0x60, hex(ctx.mode.value)

        # --- arm 0: gate clear skips slew and the +0x10a advance -------------
        ctx = Ctx()
        set_cfg_u32(ctx.cfg, 0x528, 0x10)
        set_obj_u16(ctx.obj, 0x172, 1)
        set_state_gate(ctx.state, 1, 0)
        set_obj_u16(ctx.obj, 0x184, 0x50)
        set_obj_u16(ctx.obj, 0x34, 0x10)
        set_obj_u16(ctx.obj, 0x2e, 0x800)
        set_obj_u16(ctx.obj, 0x10a, 0x20)
        ctx.mode.value = 0x30
        arm0(ctx.obj, ctx.state, ctypes.byref(ctx.mode))
        assert obj_u16(ctx.obj, 0x2e) == 0x800
        assert obj_u16(ctx.obj, 0x184) == 0x50
        assert ctx.mode.value == 0x40, hex(ctx.mode.value)

        # --- arm 0: gate clear, unsaturated mode-target turn -----------------
        ctx = Ctx()
        set_cfg_u32(ctx.cfg, 0x528, 0x100)
        set_obj_u16(ctx.obj, 0x172, 3)
        set_state_gate(ctx.state, 3, 0)
        set_obj_u16(ctx.obj, 0x184, 0x50)
        set_obj_u16(ctx.obj, 0x34, 0x10)
        set_obj_u16(ctx.obj, 0x2e, 0x800)
        ctx.mode.value = 0x40
        arm0(ctx.obj, ctx.state, ctypes.byref(ctx.mode))
        assert obj_u16(ctx.obj, 0x2e) == 0x800
        assert obj_u16(ctx.obj, 0x184) == 0x50
        assert ctx.mode.value == 0x50, hex(ctx.mode.value)

        # --- arm 12: within-limit quadrant rescale (+0x19c set) --------------
        # response 0x500, +0x2e 0x4F0 -> raw 0x10 within +/-cfg+0x52c.
        # (0x500 + 0x400) & 0xffff = 0x900 > 0x800 and +0x19c set -> x0.75.
        ctx = Ctx()
        set_cfg_u32(ctx.cfg, 0x52c, 0x100)
        set_obj_u16(ctx.obj, 0x84, 0x500)
        set_obj_u16(ctx.obj, 0x2e, 0x4F0)
        set_obj_u16(ctx.obj, 0x19c, 1)
        set_obj_u16(ctx.obj, 0x1b2, 0x1234)
        set_obj_u32(ctx.obj, 0x1c4, bits(4.0))
        arm12(ctx.obj)
        assert float_of(ctypes.cast(ctypes.byref(ctx.obj, 0x1c4),
                                    ctypes.POINTER(ctypes.c_uint32))[0]) == 3.0
        assert obj_u16(ctx.obj, 0x2e) == 0x500
        assert obj_u16(ctx.obj, 0x184) == 0x500
        assert obj_u16(ctx.obj, 0x1b2) == 0

        # --- arm 12: within-limit without +0x19c keeps +0x1c4 ----------------
        ctx = Ctx()
        set_cfg_u32(ctx.cfg, 0x52c, 0x100)
        set_obj_u16(ctx.obj, 0x84, 0x500)
        set_obj_u16(ctx.obj, 0x2e, 0x4F0)
        set_obj_u16(ctx.obj, 0x19c, 0)
        set_obj_u16(ctx.obj, 0x1b2, 0x1234)
        set_obj_u32(ctx.obj, 0x1c4, bits(4.0))
        arm12(ctx.obj)
        assert obj_u16(ctx.obj, 0x2e) == 0x500
        assert obj_u16(ctx.obj, 0x184) == 0x500
        assert obj_u16(ctx.obj, 0x1b2) == 0
        assert ctypes.cast(ctypes.byref(ctx.obj, 0x1c4),
                           ctypes.POINTER(ctypes.c_uint32))[0] == bits(4.0)

        # --- arm 12: quadrant test fails, no rescale -------------------------
        # (0x100 + 0x400) & 0xffff = 0x500 <= 0x800 -> skip even with +0x19c.
        ctx = Ctx()
        set_cfg_u32(ctx.cfg, 0x52c, 0x100)
        set_obj_u16(ctx.obj, 0x84, 0x100)
        set_obj_u16(ctx.obj, 0x2e, 0x0F0)
        set_obj_u16(ctx.obj, 0x19c, 1)
        set_obj_u16(ctx.obj, 0x1b2, 0x4321)
        set_obj_u32(ctx.obj, 0x1c4, bits(4.0))
        arm12(ctx.obj)
        assert obj_u16(ctx.obj, 0x2e) == 0x100
        assert obj_u16(ctx.obj, 0x184) == 0x100
        assert obj_u16(ctx.obj, 0x1b2) == 0
        assert ctypes.cast(ctypes.byref(ctx.obj, 0x1c4),
                           ctypes.POINTER(ctypes.c_uint32))[0] == bits(4.0)

        # --- arm 12: high saturation rescales by 0.5, leaves +0x1b2 ----------
        ctx = Ctx()
        set_cfg_u32(ctx.cfg, 0x52c, 0x100)
        set_obj_u16(ctx.obj, 0x84, 0x500)
        set_obj_u16(ctx.obj, 0x2e, 0x100)
        set_obj_u16(ctx.obj, 0x19c, 1)
        set_obj_u16(ctx.obj, 0x1b2, 0x1234)
        set_obj_u32(ctx.obj, 0x1c4, bits(4.0))
        arm12(ctx.obj)
        assert obj_u16(ctx.obj, 0x2e) == 0x200, hex(obj_u16(ctx.obj, 0x2e))
        assert obj_u16(ctx.obj, 0x184) == 0x200
        assert obj_u16(ctx.obj, 0x1b2) == 0x1234
        assert float_of(ctypes.cast(ctypes.byref(ctx.obj, 0x1c4),
                                    ctypes.POINTER(ctypes.c_uint32))[0]) == 2.0

        # --- arm 12: low saturation, no rescale when +0x19c clear ------------
        ctx = Ctx()
        set_cfg_u32(ctx.cfg, 0x52c, 0x100)
        set_obj_u16(ctx.obj, 0x84, 0x100)
        set_obj_u16(ctx.obj, 0x2e, 0x500)
        set_obj_u16(ctx.obj, 0x19c, 0)
        set_obj_u16(ctx.obj, 0x1b2, 0x7777)
        set_obj_u32(ctx.obj, 0x1c4, bits(4.0))
        arm12(ctx.obj)
        assert obj_u16(ctx.obj, 0x2e) == 0x400, hex(obj_u16(ctx.obj, 0x2e))
        assert obj_u16(ctx.obj, 0x184) == 0x400
        assert obj_u16(ctx.obj, 0x1b2) == 0x7777
        assert ctypes.cast(ctypes.byref(ctx.obj, 0x1c4),
                           ctypes.POINTER(ctypes.c_uint32))[0] == bits(4.0)

        # --- arm 12: the response is the cached +0x84, not +0x7c -------------
        ctx = Ctx()
        set_cfg_u32(ctx.cfg, 0x52c, 0x100)
        set_obj_u16(ctx.obj, 0x7c, 0x9999)
        set_obj_u16(ctx.obj, 0x84, 0x500)
        set_obj_u16(ctx.obj, 0x2e, 0x4F0)
        set_obj_u16(ctx.obj, 0x19c, 0)
        arm12(ctx.obj)
        assert obj_u16(ctx.obj, 0x2e) == 0x500
        assert obj_u16(ctx.obj, 0x184) == 0x500

        # --- arm 12: the _run wrapper mirrors the core -----------------------
        ctx = Ctx()
        set_cfg_u32(ctx.cfg, 0x52c, 0x100)
        set_obj_u16(ctx.obj, 0x84, 0x500)
        set_obj_u16(ctx.obj, 0x2e, 0x100)
        set_obj_u16(ctx.obj, 0x19c, 1)
        set_obj_u16(ctx.obj, 0x1b2, 0x1234)
        set_obj_u32(ctx.obj, 0x1c4, bits(4.0))
        arm12_run(ctx.obj)
        assert obj_u16(ctx.obj, 0x2e) == 0x200
        assert obj_u16(ctx.obj, 0x184) == 0x200
        assert obj_u16(ctx.obj, 0x1b2) == 0x1234

    # --- source evidence -----------------------------------------------------
    text = SOURCE.read_text(encoding="utf-8")
    for fragment in (
            "0x6c", "0x528", "0x52c", "0x300", "0x10a",
            "0x184", "0x2e", "0x1c4", "0x1b2", "0x19c",
            "0x32564", "0x504be0", "0x504b90", "0x884000",
            "RECOVERED_LOCOMOTION_ACTION_TURN_LIMIT",
            "RECOVERED_LOCOMOTION_ACTION_SNAP_LIMIT",
            "recovered_locomotion_action_0_run",
            "recovered_locomotion_action_12_run",
            "0x6f6f0"):
        if fragment not in text:
            raise AssertionError(
                f"locomotion actions model missing {fragment}")

    # --- listing evidence: arm 0 0x329c4-0x32a88 -----------------------------
    listing = LISTING.read_text(encoding="utf-8")
    arm0_start = listing.index("   329c4:")
    arm0_end = listing.index("   32a88:", arm0_start)
    arm0_block = listing[arm0_start:arm0_end]
    for evidence in (
            "ldos\t0x172(g0),g4", "shlo\t16,g4,g4", "shri\t12,g4,g4",
            "ld\t0x32564(g4),g4", "cmpibe\t0,g4,0x32a4c",
            "ldos\t0x34(g0),g5", "ldos\t0x184(g0),g4", "ldos\t0x2e(g0),g6",
            "shlo\t8,3,g7", "cmpi\tg7,g4", "lda\t0xfffffd00,g5",
            "cmpibge\tg4,g5,0x32a20", "addo\tg6,g4,g4", "stos\tg4,0x2e(g0)",
            "ldos\t0x10a(g0),g5", "stos\tg4,0x184(g0)",
            "ld\t0x51ab14,g7", "ldos\t0x1a(g3),g4", "ld\t0x528(g7),g6",
            "subo\tg4,g5,g5", "cmpibge\tg1,g4,0x32cec"):
        if evidence not in arm0_block:
            raise AssertionError(
                f"locomotion action-0 listing evidence missing: {evidence}")

    # --- listing evidence: arm 12 0x32ea4-0x32fd0 ----------------------------
    arm12_start = listing.index("   32ea4:")
    arm12_end = listing.index("   32fd0:", arm12_start)
    arm12_block = listing[arm12_start:arm12_end]
    for evidence in (
            "ld\t0xa8(g0),g5", "ld\t0x10(g0),g7", "ld\t0x8(g0),g4",
            "ld\t0xa4(g0),g6", "mov\t10,r10", "st\tr10,0x884000",
            "subr\tg6,g4,g4", "subr\tg7,g5,g5", "ld\t0x51ab14,g7",
            "ld\t0x884000,g5", "ldos\t0x2e(g0),g4", "ld\t0x52c(g7),g6",
            "subo\tg4,g5,g5", "shlo\t16,g5,g4", "shri\t16,g4,g1",
            "cmpi\tg6,g1", "ldos\t0x19c(g0),g4", "cmpibe\t0,g4,0x32fc4",
            "ld\t0x1c4(g0),g4", "movr\tg4,fp0", "lda\t0x3fe00000,g5",
            "mulrl\tfp0,g4,g4", "st\tg4,0x1c4(g0)", "lda\t0x3fe80000,g5",
            "addo\tg6,g4,g4", "stos\tg14,0x1b2(g0)", "stos\tg4,0x184(g0)"):
        if evidence not in arm12_block:
            raise AssertionError(
                f"locomotion action-12 listing evidence missing: {evidence}")

    print("PASS: recovered locomotion action arms 0 and 12")


if __name__ == "__main__":
    main()
