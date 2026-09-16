#!/usr/bin/env python3
"""Validate the runnable i960 locomotion state handlers 31 (0x30660) and
34 (0x30e40).

The recovered unit reads its config block through object+0x6c and keeps the
listing's absolute scratch cells (0x51ab08/0x51ab0c/0x51ab10/0x51ab12) as
file-static stand-ins, so both entry points can be driven directly.  A 0x600
object, a config block and a clip record are mapped below 4 GiB so the 32-bit
config pointer field round-trips exactly.

Covered:
  * state 31 +0x1c4 for every +0x174 0/1/2/3 x +0x176 0/1/2 combination
    (cfg+0x56c/0x570/0x574 default and cfg+0x578..0x598 selectors);
  * the state-31 +0x17e == 4 transition to +0x172 = 0 / +0x170 = 1;
  * state 34 +0x1c4 for +0x176 0/1/2 (cfg+0x570/0x574/0x56c);
  * the state-34 clip end (+0x172 = 31, +0x170 = 0, +0x17a = 0, +0x17e = 1)
    and the pre-clip +0x17a advance.
"""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_locomotion_states.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

OBJECT_SIZE = 0x600
CONFIG_SIZE = 0x700
MAP_SIZE = 0x2000

PROT_READ = 0x1
PROT_WRITE = 0x2
MAP_PRIVATE = 0x02
MAP_ANONYMOUS = 0x20
MAP_32BIT = 0x40


def mmap32(size):
    libc = ctypes.CDLL("libc.so.6", use_errno=True)
    libc.mmap.restype = ctypes.c_void_p
    libc.mmap.argtypes = [
        ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int,
        ctypes.c_int, ctypes.c_int, ctypes.c_long,
    ]
    address = libc.mmap(
        None, size, PROT_READ | PROT_WRITE,
        MAP_PRIVATE | MAP_ANONYMOUS | MAP_32BIT, -1, 0,
    )
    if not address or address == ctypes.c_void_p(-1).value:
        raise AssertionError("MAP_32BIT mmap failed")
    if address >= (1 << 32):
        raise AssertionError("mapped object above the 32-bit boundary")
    return address


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "locomotion-states.so"
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared",
             "-fPIC", "-O2", str(SOURCE), "-o", str(library)],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))

        run31 = recovered.recovered_locomotion_state_31_run
        run31.argtypes = [ctypes.c_void_p]
        run31.restype = None
        run34 = recovered.recovered_locomotion_state_34_run
        run34.argtypes = [ctypes.c_void_p]
        run34.restype = None

        base = mmap32(MAP_SIZE)
        object_base = base
        config_base = base + 0x800
        record_base = base + 0x1000

        def r8(address):
            return ctypes.c_uint8.from_address(address).value

        def r16(address):
            return ctypes.c_uint16.from_address(address).value

        def r32(address):
            return ctypes.c_uint32.from_address(address).value

        def w8(address, value):
            ctypes.c_uint8.from_address(address).value = value & 0xFF

        def w16(address, value):
            ctypes.c_uint16.from_address(address).value = value & 0xFFFF

        def w32(address, value):
            ctypes.c_uint32.from_address(address).value = value & 0xFFFFFFFF

        def cfg_word(offset):
            return 0xA5A50000 | offset

        def setup_config():
            for offset in (
                    0x56c, 0x570, 0x574, 0x578, 0x57c, 0x580, 0x584, 0x588,
                    0x58c, 0x590, 0x594, 0x598,
                    0x5e8, 0x5ec, 0x5f0, 0x5f4, 0x5f8, 0x5fc,
                    0x600, 0x604, 0x608):
                w32(config_base + offset, cfg_word(offset))
            for index in range(4):
                for table in (0xf8, 0xfc, 0x100, 0x104, 0x108, 0x10c):
                    w32(config_base + table + 32 * index, record_base)
                w32(config_base + 0x184 + 24 * index, record_base)
            w32(config_base + 0x3cc, 0)
            w32(config_base + 0x3d0, 0)
            w32(config_base + 0x3d4, 0)
            w32(config_base + 0x658, 0)
            w32(config_base + 0x660, 0xFFFFFFFF)

        def reset_object():
            for offset in range(0, OBJECT_SIZE, 4):
                w32(object_base + offset, 0)
            w32(object_base + 0x6c, config_base)

        setup_config()

        # --- state 31: +0x1c4 selector table -------------------------------
        selectors = [
            (0, 0, 0x570), (0, 1, 0x574), (0, 2, 0x56c),
            (1, 0, 0x57c), (1, 1, 0x580), (1, 2, 0x578),
            (2, 0, 0x588), (2, 1, 0x58c), (2, 2, 0x584),
            (3, 0, 0x594), (3, 1, 0x598), (3, 2, 0x590),
        ]
        for f174, f176, offset in selectors:
            reset_object()
            w16(record_base + 4, 1)
            w16(object_base + 0x17e, 0)
            w16(object_base + 0x174, f174)
            w16(object_base + 0x176, f176)
            run31(ctypes.c_void_p(object_base))
            actual = r32(object_base + 0x1c4)
            if actual != cfg_word(offset):
                raise AssertionError(
                    f"state31 +0x174={f174} +0x176={f176}: expected "
                    f"0x{cfg_word(offset):08x}, got 0x{actual:08x}")

        # --- state 31: weapon sentinel writes +0x174 ------------------------
        reset_object()
        w16(record_base + 4, 1)
        w16(object_base + 0x139, 0xff)
        w8(object_base + 0x1dd, 1)
        run31(ctypes.c_void_p(object_base))
        if r16(object_base + 0x174) != 2:
            raise AssertionError("state31 weapon gate did not select +0x174 = 2")
        if r32(object_base + 0x1c4) != cfg_word(0x588):
            raise AssertionError("state31 gated +0x174 = 2 selected wrong cfg")

        # --- state 31: +0x17e == 4 transition -------------------------------
        reset_object()
        w16(record_base + 4, 1)
        w16(object_base + 0x174, 0)
        w16(object_base + 0x176, 0)
        w16(object_base + 0x17e, 4)
        run31(ctypes.c_void_p(object_base))
        if r16(object_base + 0x172) != 0:
            raise AssertionError("state31 +0x17e==4 did not set +0x172 = 0")
        if r16(object_base + 0x170) != 1:
            raise AssertionError("state31 +0x17e==4 did not set +0x170 = 1")
        if r16(object_base + 0x17e) != 4:
            raise AssertionError("state31 +0x17e==4 advanced the counter")
        if r8(object_base + 0x1a8) != 2:
            raise AssertionError("state31 +0x17e==4 did not set +0x1a8 = 2")
        if r32(object_base + 0x1c4) != cfg_word(0x570):
            raise AssertionError("state31 +0x17e==4 tail selected wrong cfg")

        # --- state 34: +0x1c4 override and clip end -------------------------
        for f176, offset in ((0, 0x570), (1, 0x574), (2, 0x56c)):
            reset_object()
            w16(record_base + 4, 1)
            w16(object_base + 0x176, f176)
            w16(object_base + 0x17a, 0)
            run34(ctypes.c_void_p(object_base))
            actual = r32(object_base + 0x1c4)
            if actual != cfg_word(offset):
                raise AssertionError(
                    f"state34 +0x176={f176}: expected "
                    f"0x{cfg_word(offset):08x}, got 0x{actual:08x}")
            if r16(object_base + 0x172) != 31:
                raise AssertionError("state34 clip end did not set +0x172 = 31")
            if r16(object_base + 0x170) != 0:
                raise AssertionError("state34 clip end did not set +0x170 = 0")
            if r16(object_base + 0x17a) != 0:
                raise AssertionError("state34 clip end did not set +0x17a = 0")
            if r16(object_base + 0x17e) != 1:
                raise AssertionError("state34 clip end did not set +0x17e = 1")
            if r8(object_base + 0x1a8) != 1 or r8(object_base + 0x1a9) != 1:
                raise AssertionError("state34 clip end did not arm +0x1a8/+0x1a9")

        # --- state 34: +0x17a advance before the clip end -------------------
        reset_object()
        w16(record_base + 4, 5)
        w16(object_base + 0x176, 0)
        w16(object_base + 0x17a, 0)
        w16(object_base + 0x172, 0xABCD)
        run34(ctypes.c_void_p(object_base))
        if r16(object_base + 0x17a) != 1:
            raise AssertionError("state34 did not advance +0x17a")
        if r16(object_base + 0x172) != 0xABCD:
            raise AssertionError("state34 advanced past the clip end too early")
        if r32(object_base + 0x1c4) != cfg_word(0x570):
            raise AssertionError("state34 advance selected wrong cfg")

    # --- source constants ---------------------------------------------------
    text = SOURCE.read_text(encoding="utf-8")
    for fragment in (
            "recovered_locomotion_state_31_run",
            "recovered_locomotion_state_34_run",
            "RECOVERED_LOCOMOTION_CONFIG_OFFSET 0x6cU",
            "0x570U", "0x574U", "0x56cU", "0x578U", "0x580U", "0x57cU",
            "0x588U", "0x58cU", "0x584U", "0x594U", "0x598U", "0x590U",
            "0x5e8U", "0x5ecU", "0x5f0U", "0x604U", "0x608U", "0x600U",
            "0x13aU", "0x139U", "0x138U", "0x13cU", "0x1dfU", "0x1ddU",
            "0x1deU"):
        if fragment not in text:
            raise AssertionError(
                f"locomotion states model missing {fragment}")

    # --- listing evidence (0x30660-0x30c20 and 0x30e40-0x30ff0) -------------
    listing = LISTING.read_text(encoding="utf-8")
    state31 = listing[listing.index("   30660:"):listing.index("   30c20:")]
    state34 = listing[listing.index("   30e40:"):listing.index("   30ff0:")]

    for evidence in (
            "ldos\t0x17e(g0),g4", "shlo\t16,g4,g4", "bge\t0x306e8",
            "ldob\t0x13a(g0),g4", "ldob\t0x1df(g0),g4", "bbc\t0,g4,0x30904",
            "cmpibne\t4,g4,0x30ac4", "stos\tg14,0x172(g0)",
            "st\tg14,0x1c4(g0)", "ld\t0x570(g4),g4",
            "ld\t0x574(g4),g4", "ld\t0x56c(g4),g4",
            "ld\t0x57c(g4),g4", "ld\t0x580(g4),g4", "ld\t0x578(g4),g4",
            "ld\t0x594(g4),g4", "ld\t0x598(g4),g4", "ld\t0x590(g4),g4",
            "ld\t0x5ec(g4),g4", "ld\t0x5f0(g4),g4", "ld\t0x5e8(g4),g4",
            "ld\t0x604(g4),g4", "ld\t0x608(g4),g4", "ld\t0x600(g4),g4",
            "st\tg4,0x1c4(r4)"):
        if evidence not in state31:
            raise AssertionError(
                f"locomotion state 31 listing evidence missing: {evidence}")

    for evidence in (
            "lda\t0x30fec,g14", "mov\t0,g14", "stos\tg14,0x170(g0)",
            "lda\t(g4)[g4*2],g4", "ld\t0x180(g7)[g4*8],g6",
            "ld\t0x184(g7)[g4*8],g5", "cmpi\tg4,0",
            "ld\t0x570(g7),g7", "ld\t0x574(g7),g7", "ld\t0x56c(g7),g7",
            "st\tg7,0x1c4(g0)", "ldob\t0x13a(g0),g4",
            "mov\t31,g1", "stos\tg1,0x172(g0)", "stos\tg14,0x170(g0)",
            "stos\tg14,0x17a(g0)", "mov\t1,g1", "stos\tg1,0x17e(g0)",
            "stob\tg1,0x1a8(g0)", "stob\tg1,0x1a9(g0)",
            "ld\t0x658(g7),g5", "ld\t0x660(g7),g6"):
        if evidence not in state34:
            raise AssertionError(
                f"locomotion state 34 listing evidence missing: {evidence}")

    print("recovered locomotion states 31/34 runnable: ok")


if __name__ == "__main__":
    main()
