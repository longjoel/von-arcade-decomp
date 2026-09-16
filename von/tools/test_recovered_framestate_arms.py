#!/usr/bin/env python3
"""Validate the recovered i960 0x37130 frame-step arm 15 (0x36690-0x367ec).

Compiles von/i960/recovered_framestate_arms.c with
    cc -std=c11 -Wall -Wextra -Werror -shared -fPIC
and drives the pure core against a plain object plus the two direction tables.

Covered listing spans:
    0x366a0-0x3671c   +0x137 != 0xff -> state 34 + direction tables
    0x36720-0x36740   +0x102 bit 15 -> state 0 / mode 1
    0x36744-0x367d4   +0x102-keyed +0x188 classifier
    0x367d8-0x367e8   +0x1a8 0 -> 2 sentinel
"""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_framestate_arms.c"

CC = ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC"]

OBJ_SIZE = 0x600
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


class FrameStateContext(ctypes.Structure):
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


def u8(ptr, offset):
    return ctypes.cast(ctypes.byref(ptr, offset),
                       ctypes.POINTER(ctypes.c_ubyte))[0]


def set_u8(ptr, offset, value):
    ctypes.cast(ctypes.byref(ptr, offset),
                ctypes.POINTER(ctypes.c_ubyte))[0] = value & 0xff


class Ctx:
    def __init__(self):
        self.obj = low_buffer(OBJ_SIZE)
        self.cfg = low_buffer(0x800)
        self.t350 = (ctypes.c_uint16 * TABLE_COUNT)()
        self.t360 = (ctypes.c_uint16 * TABLE_COUNT)()
        self.t370 = (ctypes.c_uint16 * TABLE_COUNT)()
        set_u32(self.obj, 0x6c, ctypes.addressof(self.cfg))

    def ctx(self):
        return FrameStateContext(
            ctypes.cast(self.t350, ctypes.POINTER(ctypes.c_uint16)),
            ctypes.cast(self.t360, ctypes.POINTER(ctypes.c_uint16)),
            ctypes.cast(self.t370, ctypes.POINTER(ctypes.c_uint16)))


def set_u32(ptr, offset, value):
    ctypes.cast(ctypes.byref(ptr, offset),
                ctypes.POINTER(ctypes.c_uint32))[0] = value & 0xffffffff


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "framestate-arms.so"
        subprocess.run(CC + [str(SOURCE), "-o", str(library)], check=True)
        recovered = ctypes.CDLL(str(library))

        arm15 = recovered.recovered_framestate_state_15
        arm15.argtypes = [ctypes.POINTER(ctypes.c_ubyte),
                          ctypes.POINTER(FrameStateContext)]
        arm15.restype = ctypes.c_uint32
        run15 = recovered.recovered_framestate_state_15_run
        run15.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        run15.restype = ctypes.c_uint32

        def call(c):
            return arm15(c.obj, ctypes.byref(c.ctx()))

        # --- action != 0xff -> state 34 + tables ---------------------------
        c = Ctx()
        set_u8(c.obj, 0x137, 5)
        set_u16(c.obj, 0x184, 0x0200)
        c.t350[5] = 0x0077
        c.t360[5] = 0x0020
        assert call(c) == 1
        assert u16(c.obj, 0x172) == 34, hex(u16(c.obj, 0x172))
        assert u16(c.obj, 0x170) == 0, hex(u16(c.obj, 0x170))
        assert u16(c.obj, 0x176) == 0x0077, hex(u16(c.obj, 0x176))
        assert u16(c.obj, 0x188) == 0x0077, hex(u16(c.obj, 0x188))
        assert u16(c.obj, 0x3c) == 0x0220, hex(u16(c.obj, 0x3c))
        assert u16(c.obj, 0x186) == 0, hex(u16(c.obj, 0x186))
        assert u8(c.obj, 0x1a8) == 1 and u8(c.obj, 0x1a9) == 1

        # --- action == 0xff, +0x102 bit 15 -> state 0 / mode 1 -------------
        c = Ctx()
        set_u8(c.obj, 0x137, 0xff)
        set_u16(c.obj, 0x102, 0x8000)
        assert call(c) == 0
        assert u16(c.obj, 0x172) == 0, hex(u16(c.obj, 0x172))
        assert u16(c.obj, 0x170) == 1, hex(u16(c.obj, 0x170))

        # --- action 0xff, +0x102 small -> +0x188 = 2 -----------------------
        c = Ctx()
        set_u8(c.obj, 0x137, 0xff)
        set_u16(c.obj, 0x102, 0x1800)
        set_u16(c.obj, 0x186, 0)
        set_u8(c.obj, 0x1a8, 1)
        assert call(c) == 0
        assert u16(c.obj, 0x186) == 0x1800, hex(u16(c.obj, 0x186))
        assert u16(c.obj, 0x188) == 2, hex(u16(c.obj, 0x188))
        assert u8(c.obj, 0x1a8) == 2, hex(u8(c.obj, 0x1a8))

        # --- action 0xff, +0x102 mid -> +0x188 = 0 -------------------------
        c = Ctx()
        set_u8(c.obj, 0x137, 0xff)
        set_u16(c.obj, 0x102, 0x0100)
        set_u16(c.obj, 0x186, 0)
        assert call(c) == 0
        assert u16(c.obj, 0x188) == 0, hex(u16(c.obj, 0x188))

        # --- action 0xff, +0x102 high band -> +0x188 = 3 -------------------
        c = Ctx()
        set_u8(c.obj, 0x137, 0xff)
        set_u16(c.obj, 0x102, 0x6000)
        set_u16(c.obj, 0x186, 0)
        assert call(c) == 0
        assert u16(c.obj, 0x188) == 3, hex(u16(c.obj, 0x188))

        # --- arm 16: action -> state 34, +0x186 from 0x18370 ----------------
        arm16 = recovered.recovered_framestate_state_16
        arm16.argtypes = [ctypes.POINTER(ctypes.c_ubyte),
                          ctypes.POINTER(FrameStateContext)]
        arm16.restype = ctypes.c_uint32
        c = Ctx()
        set_u8(c.obj, 0x137, 5)
        set_u16(c.obj, 0x184, 0x0200)
        c.t350[5] = 0x0077
        c.t360[5] = 0x0020
        c.t370[5] = 0x0008
        assert arm16(c.obj, ctypes.byref(c.ctx())) == 1
        assert u16(c.obj, 0x172) == 34, hex(u16(c.obj, 0x172))
        assert u16(c.obj, 0x176) == 0x0077, hex(u16(c.obj, 0x176))
        assert u16(c.obj, 0x3c) == 0x0220, hex(u16(c.obj, 0x3c))
        assert u16(c.obj, 0x186) == 0x0004, hex(u16(c.obj, 0x186))
        assert u8(c.obj, 0x1a8) == 2

        # --- arm 16: 0xff + +0x102 bit15 + mode 2 -> state 17 ---------------
        c = Ctx()
        set_u8(c.obj, 0x137, 0xff)
        set_u16(c.obj, 0x102, 0x8000)
        set_u16(c.obj, 0x170, 2)
        assert arm16(c.obj, ctypes.byref(c.ctx())) == 0
        assert u16(c.obj, 0x172) == 17, hex(u16(c.obj, 0x172))

        # --- arm 17: action -> state 31 + accumulator -----------------------
        arm17 = recovered.recovered_framestate_state_17
        arm17.argtypes = [ctypes.POINTER(ctypes.c_ubyte),
                          ctypes.POINTER(FrameStateContext)]
        arm17.restype = ctypes.c_uint32
        c = Ctx()
        set_u32(c.cfg, 0x658, 10)
        set_u32(c.cfg, 0x660, 1000)
        set_u8(c.obj, 0x137, 5)
        set_u16(c.obj, 0x184, 0x0200)
        set_u16(c.obj, 0x4e, 0)
        c.t350[5] = 0x0077
        c.t360[5] = 0x0020
        assert arm17(c.obj, ctypes.byref(c.ctx())) == 1
        assert u16(c.obj, 0x172) == 31, hex(u16(c.obj, 0x172))
        assert u16(c.obj, 0x176) == 0x0077, hex(u16(c.obj, 0x176))
        assert u16(c.obj, 0x3c) == 0x0220, hex(u16(c.obj, 0x3c))
        assert u16(c.obj, 0x186) == 0, hex(u16(c.obj, 0x186))
        assert u16(c.obj, 0x4e) == 10, hex(u16(c.obj, 0x4e))

        # --- arm 17: 0xff classifier -> state 16 ----------------------------
        c = Ctx()
        set_u8(c.obj, 0x137, 0xff)
        set_u16(c.obj, 0x102, 0x0100)
        assert arm17(c.obj, ctypes.byref(c.ctx())) == 0
        assert u16(c.obj, 0x172) == 16, hex(u16(c.obj, 0x172))
        assert u16(c.obj, 0x188) == 0, hex(u16(c.obj, 0x188))

    print("PASS: recovered i960 frame-step arms 15/16/17 (0x36690-0x36ae4)")


if __name__ == "__main__":
    main()
