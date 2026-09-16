#!/usr/bin/env python3
"""Validate the recovered i960 committed-action -> state-31 transition (0x36460).

Compiles von/i960/recovered_action_31.c with
    cc -std=c11 -Wall -Wextra -Werror -shared -fPIC
and drives the pure core against a MAP_32BIT object plus a config block and the
three direction tables.  The config value at +0x658/+0x660 is read directly, so
the config only needs to live in a 32-bit mapping.

Covered listing spans:
    0x36470-0x36484   +0x18e cooldown gate
    0x36488-0x36498   +0x137 == 0xff leaves the object untouched
    0x3649c-0x364fc   action -> state 31, +0x176/+0x188/+0x3c/+0x186
    0x36500-0x36518   scratch clears + +0x1a8/+0x1a9
    0x3651c-0x36550   object+0x4e accumulator
"""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_action_31.c"

CC = ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC"]

OBJ_SIZE = 0x600
CFG_SIZE = 0x800
TABLE_COUNT = 0x100

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


class Action31Context(ctypes.Structure):
    _fields_ = [
        ("table_18350", ctypes.POINTER(ctypes.c_uint16)),
        ("table_18360", ctypes.POINTER(ctypes.c_uint16)),
        ("table_18370", ctypes.POINTER(ctypes.c_uint16)),
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


def u8(ptr, offset):
    return ctypes.cast(ctypes.byref(ptr, offset),
                       ctypes.POINTER(ctypes.c_ubyte))[0]


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
        self.t350 = (ctypes.c_uint16 * TABLE_COUNT)()
        self.t360 = (ctypes.c_uint16 * TABLE_COUNT)()
        self.t370 = (ctypes.c_uint16 * TABLE_COUNT)()
        set_u32(self.obj, 0x6c, ctypes.addressof(self.cfg))

    def ctx(self):
        return Action31Context(
            ctypes.cast(self.t350, ctypes.POINTER(ctypes.c_uint16)),
            ctypes.cast(self.t360, ctypes.POINTER(ctypes.c_uint16)),
            ctypes.cast(self.t370, ctypes.POINTER(ctypes.c_uint16)))


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "action-31.so"
        subprocess.run(CC + [str(SOURCE), "-o", str(library)], check=True)
        recovered = ctypes.CDLL(str(library))

        core = recovered.recovered_action_31_core
        core.argtypes = [ctypes.POINTER(ctypes.c_ubyte),
                         ctypes.POINTER(Action31Context)]
        core.restype = ctypes.c_uint32
        run = recovered.recovered_action_31_run
        run.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        run.restype = ctypes.c_uint32

        def call(c):
            return core(c.obj, ctypes.byref(c.ctx()))

        # --- action != 0xff -> state 31 + direction tables -----------------
        c = Ctx()
        set_u32(c.cfg, 0x658, 10)
        set_u32(c.cfg, 0x660, 1000)
        set_u8(c.obj, 0x137, 3)
        set_u16(c.obj, 0x184, 0x0100)
        set_u16(c.obj, 0x4e, 0)
        c.t350[3] = 0x0055
        c.t360[3] = 0x0010
        c.t370[3] = 0x0008
        assert call(c) == 1
        assert u16(c.obj, 0x172) == 31, hex(u16(c.obj, 0x172))
        assert u16(c.obj, 0x170) == 0, hex(u16(c.obj, 0x170))
        assert u16(c.obj, 0x176) == 0x0055, hex(u16(c.obj, 0x176))
        assert u16(c.obj, 0x188) == 0x0055, hex(u16(c.obj, 0x188))
        assert u16(c.obj, 0x3c) == 0x0110, hex(u16(c.obj, 0x3c))
        assert u16(c.obj, 0x186) == 0x0004, hex(u16(c.obj, 0x186))
        assert u16(c.obj, 0x4e) == 10, hex(u16(c.obj, 0x4e))
        assert u8(c.obj, 0x1a8) == 1 and u8(c.obj, 0x1a9) == 1

        # --- +0x18e cooldown: decrements and does not transition -----------
        c = Ctx()
        set_u8(c.obj, 0x137, 3)
        set_u16(c.obj, 0x18e, 5)
        set_u16(c.obj, 0x172, 9)
        assert call(c) == 0
        assert u16(c.obj, 0x18e) == 4, hex(u16(c.obj, 0x18e))
        assert u16(c.obj, 0x172) == 9, hex(u16(c.obj, 0x172))

        # --- +0x137 == 0xff leaves the object untouched --------------------
        c = Ctx()
        set_u8(c.obj, 0x137, 0xff)
        set_u16(c.obj, 0x172, 9)
        assert call(c) == 0
        assert u16(c.obj, 0x172) == 9, hex(u16(c.obj, 0x172))

        # --- accumulator clamp: step + current >= limit stops --------------
        c = Ctx()
        set_u32(c.cfg, 0x658, 10)
        set_u32(c.cfg, 0x660, 10)
        set_u8(c.obj, 0x137, 1)
        set_u16(c.obj, 0x4e, 0)
        assert call(c) == 1
        assert u16(c.obj, 0x4e) == 0, hex(u16(c.obj, 0x4e))

    print("PASS: recovered i960 committed-action -> state-31 transition (0x36460)")


if __name__ == "__main__":
    main()
