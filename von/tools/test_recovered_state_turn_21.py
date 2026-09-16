#!/usr/bin/env python3
"""Validate the recovered i960 turn/return state-21 handler (0x32120-0x32324).

Compiles von/i960/recovered_state_turn_21.c with
    cc -std=c11 -Wall -Wextra -Werror -shared -fPIC
and drives the pure core against a MAP_32BIT object plus a config block and a
published-record block.  The cfg+0x2fc lane value is dereferenced (+0x4), so the
record must live in a low mapping.

Covered listing spans:
    0x32130-0x321e4   record publication + clip-counter frame gate
    0x321e8-0x32238   +0x13b air gate -> state 11
    0x3223c-0x322f0   +0x180 sub-phase 10/11/12/else -> +0x170 1/2/3, state 0/1
    0x3231c           +0x1c4 = 0
"""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_turn_21.c"

CC = ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC"]

OBJ_SIZE = 0x600
CFG_SIZE = 0x800
RECORD_SIZE = 0x40

PROT_READ = 0x1
PROT_WRITE = 0x2
MAP_PRIVATE = 0x2
MAP_ANONYMOUS = 0x20
MAP_32BIT = 0x40


def low_buffer(size):
    libc = ctypes.CDLL(None, use_errno=True)
    libc.mmap.restype = ctypes.c_void_p
    libc.mmap.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int,
                          ctypes.c_int, ctypes.c_int, ctypes.c_long]
    addr = libc.mmap(None, size, PROT_READ | PROT_WRITE,
                     MAP_PRIVATE | MAP_ANONYMOUS | MAP_32BIT, -1, 0)
    if not addr or addr == (1 << 64) - 1:
        raise OSError(ctypes.get_errno(), "mmap MAP_32BIT failed")
    return (ctypes.c_ubyte * size).from_address(addr)


class TurnContext(ctypes.Structure):
    _fields_ = [
        ("shadow_lo", ctypes.POINTER(ctypes.c_uint32)),
        ("shadow_hi", ctypes.POINTER(ctypes.c_uint32)),
        ("counter_a", ctypes.POINTER(ctypes.c_uint16)),
        ("counter_b", ctypes.POINTER(ctypes.c_uint16)),
    ]


def u16(ptr, offset):
    return ctypes.cast(ctypes.byref(ptr, offset),
                       ctypes.POINTER(ctypes.c_uint16))[0]


def set_u16(ptr, offset, value):
    ctypes.cast(ctypes.byref(ptr, offset),
                ctypes.POINTER(ctypes.c_uint16))[0] = value & 0xffff


def set_u8(ptr, offset, value):
    ctypes.cast(ctypes.byref(ptr, offset),
                ctypes.POINTER(ctypes.c_ubyte))[0] = value & 0xff


def u32(ptr, offset):
    return ctypes.cast(ctypes.byref(ptr, offset),
                       ctypes.POINTER(ctypes.c_uint32))[0]


def set_u32(ptr, offset, value):
    ctypes.cast(ctypes.byref(ptr, offset),
                ctypes.POINTER(ctypes.c_uint32))[0] = value & 0xffffffff


class Ctx:
    def __init__(self):
        self.obj = low_buffer(OBJ_SIZE)
        self.cfg = low_buffer(CFG_SIZE)
        self.record = low_buffer(RECORD_SIZE)
        self.shadow_lo = ctypes.c_uint32(0)
        self.shadow_hi = ctypes.c_uint32(0)
        self.counter_a = ctypes.c_uint16(0xffff)
        self.counter_b = ctypes.c_uint16(0xffff)
        set_u32(self.obj, 0x6c, ctypes.addressof(self.cfg))
        set_u32(self.cfg, 0x2fc, ctypes.addressof(self.record))
        set_u16(self.record, 4, 5)

    def ctx(self):
        return TurnContext(
            ctypes.cast(ctypes.pointer(self.shadow_lo),
                        ctypes.POINTER(ctypes.c_uint32)),
            ctypes.cast(ctypes.pointer(self.shadow_hi),
                        ctypes.POINTER(ctypes.c_uint32)),
            ctypes.cast(ctypes.pointer(self.counter_a),
                        ctypes.POINTER(ctypes.c_uint16)),
            ctypes.cast(ctypes.pointer(self.counter_b),
                        ctypes.POINTER(ctypes.c_uint16)))


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "state-turn-21.so"
        subprocess.run(CC + [str(SOURCE), "-o", str(library)], check=True)
        recovered = ctypes.CDLL(str(library))

        core = recovered.recovered_state_21_core
        core.argtypes = [ctypes.POINTER(ctypes.c_ubyte),
                         ctypes.POINTER(TurnContext)]
        core.restype = None
        run = recovered.recovered_state_21_run
        run.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        run.restype = None

        def call(c):
            core(c.obj, ctypes.byref(c.ctx()))

        # --- clip frame gate: +0x17a < clip ends with +0x190 = 2 -----------
        c = Ctx()
        set_u16(c.obj, 0x17a, 0)
        set_u16(c.obj, 0x106, 0x0505)
        set_u16(c.obj, 0x108, 0x0505)
        call(c)
        assert u16(c.obj, 0x170) == 0, hex(u16(c.obj, 0x170))
        assert u16(c.obj, 0x190) == 2, hex(u16(c.obj, 0x190))
        assert u32(c.obj, 0x1c4) == 0, hex(u32(c.obj, 0x1c4))
        assert u16(c.obj, 0x17a) == 1, hex(u16(c.obj, 0x17a))
        assert c.shadow_lo.value == ctypes.addressof(c.record)
        assert c.counter_a.value == 0 and c.counter_b.value == 0
        assert u16(c.obj, 0x172) == 0, hex(u16(c.obj, 0x172))

        # --- sub-phase 10 -> +0x170 = 2, state 0 ---------------------------
        c = Ctx()
        set_u16(c.record, 4, 0)
        set_u32(c.cfg, 0x664, 0xaaaa)
        set_u16(c.obj, 0x180, 10)
        set_u16(c.obj, 0x13b, 0)
        call(c)
        assert u16(c.obj, 0x170) == 2, hex(u16(c.obj, 0x170))
        assert u16(c.obj, 0x172) == 0, hex(u16(c.obj, 0x172))
        assert u32(c.obj, 0x190) == 0xaaaa, hex(u32(c.obj, 0x190))
        assert u16(c.obj, 0x180) == 0, hex(u16(c.obj, 0x180))
        assert u32(c.obj, 0x1c4) == 0, hex(u32(c.obj, 0x1c4))

        # --- sub-phase 11 -> +0x170 = 3 ------------------------------------
        c = Ctx()
        set_u16(c.record, 4, 0)
        set_u16(c.obj, 0x180, 11)
        set_u16(c.obj, 0x13b, 0)
        call(c)
        assert u16(c.obj, 0x170) == 3, hex(u16(c.obj, 0x170))
        assert u16(c.obj, 0x172) == 0, hex(u16(c.obj, 0x172))

        # --- sub-phase 12 -> state 1 ---------------------------------------
        c = Ctx()
        set_u16(c.record, 4, 0)
        set_u16(c.obj, 0x180, 12)
        set_u16(c.obj, 0x13b, 0)
        call(c)
        assert u16(c.obj, 0x172) == 1, hex(u16(c.obj, 0x172))
        assert u16(c.obj, 0x170) == 0, hex(u16(c.obj, 0x170))

        # --- else -> +0x170 = 1, state 0, +0x190 = cfg+0x668 ----------------
        c = Ctx()
        set_u16(c.record, 4, 0)
        set_u32(c.cfg, 0x668, 0xbbbb)
        set_u16(c.obj, 0x180, 0)
        set_u16(c.obj, 0x13b, 0)
        call(c)
        assert u16(c.obj, 0x170) == 1, hex(u16(c.obj, 0x170))
        assert u16(c.obj, 0x172) == 0, hex(u16(c.obj, 0x172))
        assert u32(c.obj, 0x190) == 0xbbbb, hex(u32(c.obj, 0x190))

        # --- air gate: +0x13b set + +0x1dd bit 1 -> state 11 ---------------
        c = Ctx()
        set_u16(c.record, 4, 0)
        set_u32(c.cfg, 0x664, 0xcccc)
        set_u16(c.obj, 0x180, 0)
        set_u16(c.obj, 0x13b, 1)
        set_u8(c.obj, 0x1dd, 2)
        call(c)
        assert u16(c.obj, 0x172) == 11, hex(u16(c.obj, 0x172))
        assert u16(c.obj, 0x170) == 0, hex(u16(c.obj, 0x170))
        assert u32(c.obj, 0x190) == 0xcccc, hex(u32(c.obj, 0x190))
        assert u32(c.obj, 0x1c4) == 0, hex(u32(c.obj, 0x1c4))

    print("PASS: recovered i960 state 21 turn/return handler (0x32120-0x32324)")


if __name__ == "__main__":
    main()
