#!/usr/bin/env python3
"""Validate the recovered i960 dash/boost state-20 handler (0x31d20-0x32114).

Compiles von/i960/recovered_state_dash_20.c with
    cc -std=c11 -Wall -Wextra -Werror -shared -fPIC
and drives the pure core against a MAP_32BIT object plus a config block, a
published-record block, and the three lookup tables.  The config-table lane
value is a 32-bit pointer that the core dereferences (+0x4), so the record must
live in a low mapping.

Covered listing spans:
    0x31d30-0x31e4c   publication + cfg+0x644 frame gate
    0x31e5c-0x31f94   +0x180 sub-mode 9/10/11/12 -> states 37/38/39/40
    0x31f98-0x32090   committed-action bridge -> state 36
    0x32094-0x3210c   idle fall-through -> state 11 / 21
    0x3210c           +0x1c4 = 0
"""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_dash_20.c"

CC = ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC"]

OBJ_SIZE = 0x600
CFG_SIZE = 0x800
RECORD_SIZE = 0x40
T380_COUNT = 0x40
T350_COUNT = 0x100
T360_COUNT = 0x100

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


class DashContext(ctypes.Structure):
    _fields_ = [
        ("table_18380", ctypes.POINTER(ctypes.c_uint16)),
        ("table_18350", ctypes.POINTER(ctypes.c_uint16)),
        ("table_18360", ctypes.POINTER(ctypes.c_uint16)),
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


def u32(ptr, offset):
    return ctypes.cast(ctypes.byref(ptr, offset),
                       ctypes.POINTER(ctypes.c_uint32))[0]


def set_u32(ptr, offset, value):
    ctypes.cast(ctypes.byref(ptr, offset),
                ctypes.POINTER(ctypes.c_uint32))[0] = value & 0xffffffff


def set_u8(ptr, offset, value):
    ctypes.cast(ctypes.byref(ptr, offset),
                ctypes.POINTER(ctypes.c_ubyte))[0] = value & 0xff


class Ctx:
    def __init__(self):
        self.obj = low_buffer(OBJ_SIZE)
        self.cfg = low_buffer(CFG_SIZE)
        self.record = low_buffer(RECORD_SIZE)
        self.t380 = (ctypes.c_uint16 * T380_COUNT)()
        self.t350 = (ctypes.c_uint16 * T350_COUNT)()
        self.t360 = (ctypes.c_uint16 * T360_COUNT)()
        self.shadow_lo = ctypes.c_uint32(0)
        self.shadow_hi = ctypes.c_uint32(0)
        self.counter_a = ctypes.c_uint16(0xffff)
        self.counter_b = ctypes.c_uint16(0xffff)
        set_u32(self.obj, 0x6c, ctypes.addressof(self.cfg))
        # lane (+0x176 & 3) == 0, +0x174 != 0 uses cfg+0x294/0x290; +0x174 == 0
        # uses cfg+0x28c (word_b, dereferenced) and cfg+0x288 (word_a).
        set_u32(self.cfg, 0x28c, ctypes.addressof(self.record))
        set_u16(self.record, 4, 8)

    def ctx(self):
        return DashContext(
            ctypes.cast(self.t380, ctypes.POINTER(ctypes.c_uint16)),
            ctypes.cast(self.t350, ctypes.POINTER(ctypes.c_uint16)),
            ctypes.cast(self.t360, ctypes.POINTER(ctypes.c_uint16)),
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
        library = pathlib.Path(directory) / "state-dash-20.so"
        subprocess.run(CC + [str(SOURCE), "-o", str(library)], check=True)
        recovered = ctypes.CDLL(str(library))

        core = recovered.recovered_state_dash_20_core
        core.argtypes = [ctypes.POINTER(ctypes.c_ubyte),
                         ctypes.POINTER(DashContext)]
        core.restype = None
        run = recovered.recovered_state_dash_20_run
        run.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        run.restype = None

        def call(c):
            core(c.obj, ctypes.byref(c.ctx()))

        # --- frame gate: below cfg+0x644 ends with +0x1b2 = 5 --------------
        c = Ctx()
        set_u32(c.cfg, 0x644, 100)
        set_u16(c.obj, 0x106, 0x0abc)
        set_u16(c.obj, 0x108, 0x0abc)
        set_u16(c.obj, 0x17a, 0)
        call(c)
        assert u16(c.obj, 0x170) == 0, hex(u16(c.obj, 0x170))
        assert u16(c.obj, 0x1b2) == 5, hex(u16(c.obj, 0x1b2))
        assert u16(c.obj, 0x190) == 2, hex(u16(c.obj, 0x190))
        assert u32(c.obj, 0x1c4) == 0, hex(u32(c.obj, 0x1c4))
        # +0x17a advanced once (0x106 == 0x108)
        assert u16(c.obj, 0x17a) == 1, hex(u16(c.obj, 0x17a))
        # published record lane and clip count
        assert c.shadow_lo.value == ctypes.addressof(c.record)
        assert c.counter_a.value == 7, hex(c.counter_a.value)
        assert c.counter_b.value == 7, hex(c.counter_b.value)

        # --- +0x106 != +0x108 advances +0x17a twice ------------------------
        c = Ctx()
        set_u32(c.cfg, 0x644, 100)
        set_u16(c.obj, 0x106, 0x1111)
        set_u16(c.obj, 0x108, 0x2222)
        set_u16(c.obj, 0x17a, 0)
        call(c)
        assert u16(c.obj, 0x17a) == 2, hex(u16(c.obj, 0x17a))

        # --- sub-mode 9 -> state 37 ----------------------------------------
        c = Ctx()
        set_u32(c.cfg, 0x644, 0)
        set_u32(c.cfg, 0x668, 0xcafe)
        set_u16(c.obj, 0x174, 0)
        set_u16(c.obj, 0x176, 0)
        set_u16(c.obj, 0x180, 9)
        c.t380[0] = 0x1234
        call(c)
        assert u16(c.obj, 0x172) == 37, hex(u16(c.obj, 0x172))
        assert u16(c.obj, 0x176) == 0x1234, hex(u16(c.obj, 0x176))
        assert u16(c.obj, 0x180) == 0, hex(u16(c.obj, 0x180))
        assert u16(c.obj, 0x1b2) == 7, hex(u16(c.obj, 0x1b2))
        assert u32(c.obj, 0x190) == 0xcafe, hex(u32(c.obj, 0x190))
        assert u32(c.obj, 0x1c4) == 0, hex(u32(c.obj, 0x1c4))

        # --- sub-mode 11 with the air flag -> state 38 ---------------------
        c = Ctx()
        set_u32(c.cfg, 0x644, 0)
        set_u32(c.cfg, 0x664, 0xbeef)
        set_u16(c.obj, 0x174, 0)
        set_u16(c.obj, 0x176, 0)
        set_u16(c.obj, 0x180, 11)
        set_u8(c.obj, 0x1dd, 2)
        c.t380[0] = 0x2222
        call(c)
        assert u16(c.obj, 0x172) == 38, hex(u16(c.obj, 0x172))
        assert u16(c.obj, 0x176) == 0x2222, hex(u16(c.obj, 0x176))
        assert u32(c.obj, 0x190) == 0xbeef, hex(u32(c.obj, 0x190))
        assert u32(c.obj, 0x1c4) == 0, hex(u32(c.obj, 0x1c4))

        # --- committed action != 0xff -> state 36, tables + +0x3c ----------
        c = Ctx()
        set_u32(c.cfg, 0x644, 0)
        set_u32(c.cfg, 0x658, 10)
        set_u32(c.cfg, 0x660, 1000)
        set_u32(c.cfg, 0x668, 0x1234)
        set_u16(c.obj, 0x174, 0)
        set_u16(c.obj, 0x176, 0)
        set_u16(c.obj, 0x180, 0)
        set_u8(c.obj, 0x143, 1)
        set_u8(c.obj, 0x136, 3)
        set_u16(c.obj, 0x184, 0x0100)
        set_u16(c.obj, 0x4e, 0)
        c.t380[0] = 0x3333
        c.t350[3] = 0x0055
        c.t360[3] = 0x0010
        call(c)
        assert u16(c.obj, 0x172) == 36, hex(u16(c.obj, 0x172))
        assert u16(c.obj, 0x176) == 0x0055, hex(u16(c.obj, 0x176))
        assert u16(c.obj, 0x188) == 0x0055, hex(u16(c.obj, 0x188))
        assert u16(c.obj, 0x3c) == 0x0110, hex(u16(c.obj, 0x3c))
        assert u16(c.obj, 0x4e) == 10, hex(u16(c.obj, 0x4e))
        assert u32(c.obj, 0x190) == 0x1234, hex(u32(c.obj, 0x190))
        assert u32(c.obj, 0x1c4) == 0, hex(u32(c.obj, 0x1c4))

        # --- action 0xff, +0x13b == 0 -> state 21 --------------------------
        c = Ctx()
        set_u32(c.cfg, 0x644, 0)
        set_u16(c.obj, 0x174, 0)
        set_u16(c.obj, 0x176, 0)
        set_u16(c.obj, 0x180, 0)
        set_u8(c.obj, 0x143, 1)
        set_u8(c.obj, 0x136, 0xff)
        set_u8(c.obj, 0x13b, 0)
        c.t380[0] = 0x4444
        call(c)
        assert u16(c.obj, 0x172) == 21, hex(u16(c.obj, 0x172))
        assert u16(c.obj, 0x176) == 0x4444, hex(u16(c.obj, 0x176))
        assert u32(c.obj, 0x1c4) == 0, hex(u32(c.obj, 0x1c4))

        # --- action 0xff, +0x13b set + air flag -> state 11 ----------------
        c = Ctx()
        set_u32(c.cfg, 0x644, 0)
        set_u16(c.obj, 0x174, 0)
        set_u16(c.obj, 0x176, 0)
        set_u16(c.obj, 0x180, 0)
        set_u8(c.obj, 0x143, 1)
        set_u8(c.obj, 0x136, 0xff)
        set_u8(c.obj, 0x13b, 1)
        set_u8(c.obj, 0x1df, 2)
        call(c)
        assert u16(c.obj, 0x172) == 11, hex(u16(c.obj, 0x172))
        assert u16(c.obj, 0x176) == 0, hex(u16(c.obj, 0x176))
        assert u32(c.obj, 0x1c4) == 0, hex(u32(c.obj, 0x1c4))

    print("PASS: recovered i960 state 20 dash/boost handler (0x31d20-0x32114)")


if __name__ == "__main__":
    main()
