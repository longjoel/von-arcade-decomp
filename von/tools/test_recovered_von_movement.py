#!/usr/bin/env python3
"""Validate the shared movement kernel (von/i960/von_movement.c) on the host.

This is the same source the i960 build compiles. The object and config live in
MAP_32BIT mappings so the 32-bit config pointer at object+0x6c is valid, exactly
as the godot kernel will use it.
"""

import ctypes
import pathlib
import struct
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/von_movement.c"
HEADER = ROOT / "von/i960"

CC = ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC"]

PROT_READ = 0x1
PROT_WRITE = 0x2
MAP_PRIVATE = 0x2
MAP_ANONYMOUS = 0x20
MAP_32BIT = 0x40

TABLE_COUNT = 0x100


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


def fbits(v):
    return struct.unpack("<I", struct.pack("<f", v))[0]


def fof(w):
    return struct.unpack("<f", struct.pack("<I", w))[0]


def set_u16(buf, off, v):
    ctypes.cast(ctypes.byref(buf, off), ctypes.POINTER(ctypes.c_uint16))[0] = v


def set_u32(buf, off, v):
    ctypes.cast(ctypes.byref(buf, off), ctypes.POINTER(ctypes.c_uint32))[0] = v


def u16(buf, off):
    return ctypes.cast(ctypes.byref(buf, off), ctypes.POINTER(ctypes.c_uint16))[0]


TRIG = ctypes.CFUNCTYPE(None, ctypes.c_uint32,
                        ctypes.POINTER(ctypes.c_float),
                        ctypes.POINTER(ctypes.c_float))


class Env(ctypes.Structure):
    _fields_ = [
        ("dir_18350", ctypes.POINTER(ctypes.c_uint16)),
        ("dir_18360", ctypes.POINTER(ctypes.c_uint16)),
        ("dir_18370", ctypes.POINTER(ctypes.c_uint16)),
        ("project", ctypes.c_void_p),
        ("trig", TRIG),
    ]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "von-movement.so"
        subprocess.run(CC + ["-I", str(HEADER), str(SOURCE), "-o", str(library)],
                       check=True)
        recovered = ctypes.CDLL(str(library))
        tick = recovered.von_movement_tick
        tick.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(Env)]
        tick.restype = ctypes.c_int

        # --- action -> state 31, default speed, libm trig -------------------
        obj = low_buffer(0x600)
        cfg = low_buffer(0x800)
        t350 = (ctypes.c_uint16 * TABLE_COUNT)()
        t360 = (ctypes.c_uint16 * TABLE_COUNT)()
        t370 = (ctypes.c_uint16 * TABLE_COUNT)()
        t350[0] = 0
        t360[0] = 0
        set_u32(obj, 0x6c, ctypes.addressof(cfg))
        set_u32(cfg, 0x56c, fbits(3.5))
        set_u32(cfg, 0x570, fbits(3.2))
        set_u32(cfg, 0x574, fbits(2.0))
        set_u32(obj, 0x08, fbits(10.0))
        set_u32(obj, 0x10, fbits(20.0))
        obj[0x137] = 0  # committed action, not 0xff

        import math

        def trig(heading, sinp, cosp):
            ang = (ctypes.c_int16(heading).value) * (2.0 * math.pi / 65536.0)
            sinp[0] = math.sin(ang)
            cosp[0] = math.cos(ang)

        env = Env(ctypes.cast(t350, ctypes.POINTER(ctypes.c_uint16)),
                  ctypes.cast(t360, ctypes.POINTER(ctypes.c_uint16)),
                  ctypes.cast(t370, ctypes.POINTER(ctypes.c_uint16)),
                  None, TRIG(trig))
        assert tick(obj, ctypes.byref(env)) == 1
        assert u16(obj, 0x172) == 31, hex(u16(obj, 0x172))
        assert abs(fof(ctypes.cast(ctypes.byref(obj, 0x1c4),
                                   ctypes.POINTER(ctypes.c_uint32))[0]) - 3.2) < 1e-5
        assert abs(fof(ctypes.cast(ctypes.byref(obj, 0x1cc),
                                   ctypes.POINTER(ctypes.c_uint32))[0]) - 3.2) < 1e-5
        assert abs(fof(ctypes.cast(ctypes.byref(obj, 0x10),
                                   ctypes.POINTER(ctypes.c_uint32))[0]) - 23.2) < 1e-4

        # --- +0x176 == 1 selects cfg+0x574 (2.0) ---------------------------
        obj2 = low_buffer(0x600)
        set_u32(obj2, 0x6c, ctypes.addressof(cfg))
        set_u16(obj2, 0x172, 31)
        t350[1] = 1
        obj2[0x137] = 0xff
        set_u16(obj2, 0x176, 1)
        assert tick(obj2, ctypes.byref(env)) == 1
        assert u16(obj2, 0x172) == 31, hex(u16(obj2, 0x172))
        assert abs(fof(ctypes.cast(ctypes.byref(obj2, 0x1c4),
                                   ctypes.POINTER(ctypes.c_uint32))[0]) - 2.0) < 1e-5

        # --- trig == NULL keeps the caller's velocity ----------------------
        obj3 = low_buffer(0x600)
        set_u32(obj3, 0x6c, ctypes.addressof(cfg))
        set_u16(obj3, 0x172, 31)
        set_u16(obj3, 0x176, 0)
        obj3[0x137] = 0xff
        set_u32(obj3, 0x1c8, fbits(0.0))
        set_u32(obj3, 0x1cc, fbits(4.0))
        env2 = Env(ctypes.cast(t350, ctypes.POINTER(ctypes.c_uint16)),
                   ctypes.cast(t360, ctypes.POINTER(ctypes.c_uint16)),
                   ctypes.cast(t370, ctypes.POINTER(ctypes.c_uint16)),
                   None, TRIG())
        assert tick(obj3, ctypes.byref(env2)) == 1
        assert fof(ctypes.cast(ctypes.byref(obj3, 0x10),
                               ctypes.POINTER(ctypes.c_uint32))[0]) == 4.0

        # --- action heading offset: back (dir_18360 0x8000) -> -z -----------
        obj4 = low_buffer(0x600)
        set_u32(obj4, 0x6c, ctypes.addressof(cfg))
        set_u16(obj4, 0x172, 31)
        t360[1] = 0x8000   # 180 degrees
        obj4[0x137] = 1    # committed action = back
        set_u16(obj4, 0x184, 0)
        assert tick(obj4, ctypes.byref(env)) == 1
        vx4 = fof(ctypes.cast(ctypes.byref(obj4, 0x1c8),
                              ctypes.POINTER(ctypes.c_uint32))[0])
        vz4 = fof(ctypes.cast(ctypes.byref(obj4, 0x1cc),
                              ctypes.POINTER(ctypes.c_uint32))[0])
        assert abs(vx4) < 1e-4 and vz4 < -0.5, (vx4, vz4)

        # --- weapon gate: left weapon charging -> selector 1 -> family 1 -----
        obj5 = low_buffer(0x600)
        set_u32(obj5, 0x6c, ctypes.addressof(cfg))
        set_u16(obj5, 0x172, 31)
        set_u16(obj5, 0x176, 0)          # select 0
        obj5[0x137] = 0xff               # no movement action
        obj5[0x138] = 0xff               # left weapon available
        obj5[0x1de] = 1                  # left weapon charge flag
        set_u32(cfg, 0x57c, fbits(2.74))
        assert tick(obj5, ctypes.byref(env)) == 1
        assert abs(fof(ctypes.cast(ctypes.byref(obj5, 0x1c4),
                                   ctypes.POINTER(ctypes.c_uint32))[0]) - 2.74) < 1e-5

    print("PASS: shared movement kernel (von_movement.c) host build")


if __name__ == "__main__":
    main()
