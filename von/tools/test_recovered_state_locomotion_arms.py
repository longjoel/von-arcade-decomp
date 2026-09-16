#!/usr/bin/env python3
"""Validate the runnable i960 input-facing locomotion/idle state handlers
0 (0x2f580), 1 (0x2f930), 15 (0x2fa20), 16 (0x2fb20), 17 (0x2fd50),
32 (0x30c20) and 36 (0x31210).

Compiles von/i960/recovered_state_locomotion_arms.c with
    cc -std=c11 -Wall -Wextra -Werror -shared -fPIC
and drives the seven entry points against a locally allocated 0x600 object
plus a config block and clip records.  The object and config live in a
MAP_32BIT mapping so the config pointer stored at object+0x6c round-trips
through the unit's 32-bit load, and the clip-record pointers stored in the
config block are also 32-bit.

For each state the test asserts the +0x1b2 / +0x1c4 writes and the +0x172
transitions, plus the per-state clip counters and sentinels.  A tiny ret stub
mapped below 4 GiB stands in for the cfg callbacks so the +0x170 dispatch
paths are exercised without an external image.

Listing spans in von/build/disasm/vonj-maincpu.lst:
    0  0x2f580-0x2f92c    1  0x2f930-0x2fa14   15 0x2fa20-0x2fb10
   16 0x2fb20-0x2fd40    17 0x2fd50-0x2fe24   32 0x30c20-0x30d38
   36 0x31210-0x313d4

The 43-entry 0x32560 update table selects these on object+0x172; the 0x72ea0
input commit gate accepts a command only in +0x172 in {15,16,31}.
"""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_locomotion_arms.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

CC = ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC"]

OBJECT_SIZE = 0x600
CONFIG_SIZE = 0x800
MAP_SIZE = 0x3000

OBJECT_BASE_OFFSET = 0x0
CONFIG_BASE_OFFSET = 0x800
RECORD_BASE_OFFSET = 0x1000

# Records used by the config record slots.
REC0 = RECORD_BASE_OFFSET + 0x00
REC1 = RECORD_BASE_OFFSET + 0x40
REC_A4 = RECORD_BASE_OFFSET + 0x80
REC_B4 = RECORD_BASE_OFFSET + 0xC0
REC_74 = RECORD_BASE_OFFSET + 0x100

PROT_READ = 0x1
PROT_WRITE = 0x2
PROT_EXEC = 0x4
MAP_PRIVATE = 0x02
MAP_ANONYMOUS = 0x20
MAP_32BIT = 0x40


def mmap32(size, executable=False):
    libc = ctypes.CDLL(None, use_errno=True)
    libc.mmap.restype = ctypes.c_void_p
    libc.mmap.argtypes = [
        ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int,
        ctypes.c_int, ctypes.c_int, ctypes.c_long,
    ]
    protection = PROT_READ | PROT_WRITE | (PROT_EXEC if executable else 0)
    address = libc.mmap(
        None, size, protection,
        MAP_PRIVATE | MAP_ANONYMOUS | MAP_32BIT, -1, 0,
    )
    if not address or address == ctypes.c_void_p(-1).value:
        raise AssertionError("MAP_32BIT mmap failed")
    if address >= (1 << 32):
        raise AssertionError("mapped block above the 32-bit boundary")
    return address


def ret_stub():
    """A one-byte `ret` below 4 GiB, usable as a 32-bit cfg callback."""
    address = mmap32(0x1000, executable=True)
    ctypes.c_uint8.from_address(address).value = 0xC3
    return address


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "state-locomotion-arms.so"
        subprocess.run(CC + [str(SOURCE), "-o", str(library)], check=True)
        recovered = ctypes.CDLL(str(library))

        entry_points = {}
        for state in (0, 1, 15, 16, 17, 32, 36):
            function = getattr(
                recovered, f"recovered_state_locomotion_{state}_run")
            function.argtypes = [ctypes.c_void_p]
            function.restype = None
            entry_points[state] = function

        base = mmap32(MAP_SIZE)
        object_base = base + OBJECT_BASE_OFFSET
        config_base = base + CONFIG_BASE_OFFSET
        record_base = base + RECORD_BASE_OFFSET
        stub = ret_stub()

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

        def clear(address, size):
            for offset in range(0, size, 4):
                w32(address + offset, 0)

        def reset_object():
            clear(object_base, OBJECT_SIZE)
            w32(object_base + 0x6c, config_base)

        def setup_config():
            clear(config_base, CONFIG_SIZE)
            for offset in (
                    0x70, 0x74, 0x78, 0x7c, 0x80, 0x84, 0x98, 0x9c,
                    0xa0, 0xa4, 0xa8, 0xac, 0xb0, 0xb4,
                    0x530, 0x534, 0x538, 0x53c, 0x540, 0x544,
                    0x554, 0x558, 0x55c, 0x560, 0x564, 0x568,
                    0x56c, 0x570, 0x574, 0x658, 0x660,
                    0x3a8, 0x3ac, 0x3b0, 0x3b4, 0x3b8, 0x3bc, 0x3c0, 0x3c4,
                    0x3c8):
                w32(config_base + offset, cfg_word(offset))
            # Record slots used by the seven slices.  Indexed tables get the
            # same record for every index; the keyed tests override one slot.
            w32(config_base + 0x74, record_base + REC_74)
            w32(config_base + 0xa4, record_base + REC_A4)
            w32(config_base + 0xb4, record_base + REC_B4)
            for index in range(4):
                w32(config_base + 0x7c + 8 * index, record_base + REC0)
                w32(config_base + 0xbc + 8 * index, record_base + REC0)
                w32(config_base + 0xdc + 8 * index, record_base + REC0)
            for index in range(3):
                w32(config_base + 0x10c + 32 * index, record_base + REC0)
                w32(config_base + 0x36c + 32 * index, record_base + REC0)
                w32(config_base + 0x36c + 8 * index, record_base + REC0)
            # Callback slots default to zero so the numeric paths run.
            for slot in (0x3a8, 0x3ac, 0x3b0, 0x3b4, 0x3b8, 0x3bc,
                         0x3c0, 0x3c4, 0x3c8):
                w32(config_base + slot, 0)
            # Clip counts.
            for record in (REC0, REC1, REC_A4, REC_B4, REC_74):
                w16(record_base + record + 0x4, 5)

        def set_count(record, count):
            w16(record_base + record + 0x4, count)

        def run(state):
            entry_points[state](ctypes.c_void_p(object_base))

        # --- state 0 --------------------------------------------------------
        # +0x10e in 1..0x7fff ramps +0x194 up.
        reset_object()
        setup_config()
        w32(object_base + 0x1c4, 0xDEADBEEF)
        w16(object_base + 0x172, 0xABCD)
        w16(object_base + 0x10e, 1)
        w16(object_base + 0x194, 5)
        run(0)
        assert r16(object_base + 0x194) == 6, \
            f"state 0 positive ramp: +0x194 = {r16(object_base + 0x194)}"
        assert r16(object_base + 0x1b2) == 0, "state 0 did not clear +0x1b2"
        assert r32(object_base + 0x1c4) == 0xDEADBEEF, "state 0 wrote +0x1c4"
        assert r16(object_base + 0x172) == 0xABCD, "state 0 wrote +0x172"

        # +0x194 below -15 clamps to -15.
        reset_object()
        setup_config()
        w16(object_base + 0x10e, 1)
        w16(object_base + 0x194, 0xFFF0)
        run(0)
        assert r16(object_base + 0x194) == 0xFFF1, \
            f"state 0 clamp: +0x194 = 0x{r16(object_base + 0x194):04x}"

        # +0x10e bit 15 steps +0x194 down by 2.
        reset_object()
        setup_config()
        w16(object_base + 0x10e, 0xFFFF)
        w16(object_base + 0x194, 5)
        run(0)
        assert r16(object_base + 0x194) == 3, \
            f"state 0 negative ramp: +0x194 = {r16(object_base + 0x194)}"

        # +0x10e == 0 and +0x194 positive decrements.
        reset_object()
        setup_config()
        w16(object_base + 0x10e, 0)
        w16(object_base + 0x194, 5)
        run(0)
        assert r16(object_base + 0x194) == 4, \
            f"state 0 zero/positive: +0x194 = {r16(object_base + 0x194)}"

        # +0x10e == 0 and +0x194 negative increments.
        reset_object()
        setup_config()
        w16(object_base + 0x10e, 0)
        w16(object_base + 0x194, 0xFFFB)
        run(0)
        assert r16(object_base + 0x194) == 0xFFFC, \
            f"state 0 zero/negative: +0x194 = 0x{r16(object_base + 0x194):04x}"

        # +0x10e == 0 and +0x194 == 0: the +0x1db/+0x1dc gate bumps +0x17a.
        reset_object()
        setup_config()
        set_count(REC_74, 100)
        w16(object_base + 0x10e, 0)
        w16(object_base + 0x194, 0)
        w16(object_base + 0x17a, 7)
        w8(object_base + 0x1db, 0)
        w8(object_base + 0x1dc, 0)
        run(0)
        assert r16(object_base + 0x17a) == 8, \
            f"state 0 gate: +0x17a = {r16(object_base + 0x17a)}"

        reset_object()
        setup_config()
        set_count(REC_74, 100)
        w16(object_base + 0x10e, 0)
        w16(object_base + 0x194, 0)
        w16(object_base + 0x17a, 7)
        w8(object_base + 0x1db, 0xFA)
        run(0)
        assert r16(object_base + 0x17a) == 7, \
            "state 0 gate did not block on +0x1db > 0xf9"

        # +0x170 dispatch: a non-zero callback returns through the tail.
        reset_object()
        setup_config()
        w32(config_base + 0x3a8, stub)
        w16(object_base + 0x170, 2)
        w16(object_base + 0x10e, 1)
        w16(object_base + 0x194, 5)
        run(0)
        assert r16(object_base + 0x194) == 5, \
            "state 0 callback did not take the 0x2f928 tail"
        assert r16(object_base + 0x1b2) == 0

        # +0x170 dispatch: a zero callback falls through to the ramp.
        reset_object()
        setup_config()
        w16(object_base + 0x170, 2)
        w16(object_base + 0x10e, 1)
        w16(object_base + 0x194, 5)
        run(0)
        assert r16(object_base + 0x194) == 6, \
            "state 0 zero callback did not fall through to the ramp"

        # --- state 1 --------------------------------------------------------
        # +0x102 classification into +0x186/+0x188; +0x172 = 15.
        for word, expected in ((0x0000, 0), (0x3000, 1), (0x2000, 2),
                               (0x6000, 3)):
            reset_object()
            setup_config()
            w32(config_base + 0x3c8, stub)
            w16(object_base + 0x17c, 0xFFFF)
            w16(object_base + 0x102, word)
            w16(object_base + 0x1b2, 0xBEEF)
            w32(object_base + 0x1c4, 0xDEADBEEF)
            run(1)
            assert r16(object_base + 0x172) == 15, \
                f"state 1 +0x102=0x{word:04x}: +0x172 != 15"
            assert r16(object_base + 0x186) == word, \
                f"state 1 +0x102=0x{word:04x}: +0x186 mismatch"
            assert r16(object_base + 0x188) == expected, \
                (f"state 1 +0x102=0x{word:04x}: +0x188 = "
                 f"{r16(object_base + 0x188)} != {expected}")
            assert r16(object_base + 0x1b2) == 0xBEEF, \
                "state 1 wrote +0x1b2"
            assert r32(object_base + 0x1c4) == 0xDEADBEEF, \
                "state 1 wrote +0x1c4"

        # +0x17c != 0xffff returns immediately.
        reset_object()
        setup_config()
        w32(config_base + 0x3c8, stub)
        w16(object_base + 0x17c, 0)
        w16(object_base + 0x172, 0xABCD)
        run(1)
        assert r16(object_base + 0x172) == 0xABCD, \
            "state 1 +0x17c != 0xffff wrote +0x172"

        # +0x102 bit 15 leaves +0x172 = 0.
        reset_object()
        setup_config()
        w32(config_base + 0x3c8, stub)
        w16(object_base + 0x17c, 0xFFFF)
        w16(object_base + 0x102, 0x8000)
        w16(object_base + 0x172, 0xABCD)
        run(1)
        assert r16(object_base + 0x172) == 0, \
            "state 1 +0x102 bit 15 did not leave +0x172 = 0"

        # +0x139 != 0 leaves +0x172 = 0.
        reset_object()
        setup_config()
        w32(config_base + 0x3c8, stub)
        w16(object_base + 0x17c, 0xFFFF)
        w16(object_base + 0x139, 1)
        w16(object_base + 0x172, 0xABCD)
        run(1)
        assert r16(object_base + 0x172) == 0, \
            "state 1 +0x139 != 0 did not leave +0x172 = 0"

        # --- state 15 -------------------------------------------------------
        # Clip end sets +0x172 = 16 and +0x1c4 by +0x188.
        for f188, speed in ((0, 0x534), (1, 0x538), (2, 0x530)):
            reset_object()
            setup_config()
            set_count(REC0, 1)
            w16(object_base + 0x188, f188)
            w16(object_base + 0x17a, 0)
            run(15)
            assert r16(object_base + 0x172) == 16, \
                f"state 15 +0x188={f188}: +0x172 != 16"
            assert r16(object_base + 0x17a) == 0, \
                f"state 15 +0x188={f188}: +0x17a != 0"
            assert r32(object_base + 0x1c4) == cfg_word(speed), \
                (f"state 15 +0x188={f188}: +0x1c4 = "
                 f"0x{r32(object_base + 0x1c4):08x}")
            assert r16(object_base + 0x1b2) == 0, \
                f"state 15 +0x188={f188}: +0x1b2 != 0"

        # Advance path keeps +0x172 and bumps +0x17a.
        reset_object()
        setup_config()
        set_count(REC0, 5)
        w16(object_base + 0x188, 0)
        w16(object_base + 0x17a, 0)
        w16(object_base + 0x172, 0xABCD)
        run(15)
        assert r16(object_base + 0x17a) == 1, "state 15 did not advance +0x17a"
        assert r16(object_base + 0x172) == 0xABCD, \
            "state 15 advanced past the clip end"
        assert r32(object_base + 0x1c4) == cfg_word(0x534)
        assert r16(object_base + 0x1b2) == 0

        # The record pair is keyed by +0x188 * 8.
        reset_object()
        setup_config()
        w32(config_base + 0x7c, record_base + REC0)
        w32(config_base + 0x7c + 8, record_base + REC1)
        set_count(REC0, 100)
        set_count(REC1, 1)
        w16(object_base + 0x188, 1)
        w16(object_base + 0x17a, 0)
        run(15)
        assert r16(object_base + 0x172) == 16, \
            "state 15 +0x188=1 did not use the +0x84 record pair"
        assert r32(object_base + 0x1c4) == cfg_word(0x538)

        # --- state 16 -------------------------------------------------------
        # Default clip end selects +0x1c4 by +0x188.
        for f188, speed in ((0, 0x540), (1, 0x544), (2, 0x53c)):
            reset_object()
            setup_config()
            set_count(REC0, 0)
            w16(object_base + 0x188, f188)
            w16(object_base + 0x17a, 0)
            w16(object_base + 0x172, 0xABCD)
            run(16)
            assert r16(object_base + 0x172) == 0xABCD, \
                f"state 16 +0x188={f188}: wrote +0x172"
            assert r16(object_base + 0x17a) == 0, \
                f"state 16 +0x188={f188}: +0x17a != 0"
            assert r32(object_base + 0x1c4) == cfg_word(speed), \
                (f"state 16 +0x188={f188}: +0x1c4 = "
                 f"0x{r32(object_base + 0x1c4):08x}")
            assert r16(object_base + 0x1b2) == 0, \
                f"state 16 +0x188={f188}: +0x1b2 != 0"

        # Default advance uses +0x17a < count (no -1).
        reset_object()
        setup_config()
        set_count(REC0, 5)
        w16(object_base + 0x188, 0)
        w16(object_base + 0x17a, 0)
        run(16)
        assert r16(object_base + 0x17a) == 1, "state 16 did not advance +0x17a"

        # +0x170 dispatch with a live callback selects the 0x554..0x568 group.
        for f170, slot, f188, speed in (
                (2, 0x3ac, 0, 0x558), (2, 0x3ac, 1, 0x55c),
                (2, 0x3ac, 2, 0x554),
                (3, 0x3b4, 0, 0x564), (3, 0x3b4, 1, 0x568),
                (3, 0x3b4, 2, 0x560),
                (4, 0x3c4, 0, 0x558), (4, 0x3c4, 1, 0x55c),
                (4, 0x3c4, 2, 0x554),
                (5, 0x3bc, 0, 0x564), (5, 0x3bc, 1, 0x568),
                (5, 0x3bc, 2, 0x560)):
            reset_object()
            setup_config()
            w32(config_base + slot, stub)
            w16(object_base + 0x170, f170)
            w16(object_base + 0x188, f188)
            w16(object_base + 0x172, 0xABCD)
            run(16)
            assert r32(object_base + 0x1c4) == cfg_word(speed), \
                (f"state 16 +0x170={f170} +0x188={f188}: +0x1c4 = "
                 f"0x{r32(object_base + 0x1c4):08x}")
            assert r16(object_base + 0x172) == 0xABCD, \
                f"state 16 +0x170={f170}: wrote +0x172"
            assert r16(object_base + 0x1b2) == 0, \
                f"state 16 +0x170={f170}: +0x1b2 != 0"

        # A zero callback falls through to the default clip.
        reset_object()
        setup_config()
        set_count(REC0, 0)
        w16(object_base + 0x170, 2)
        w16(object_base + 0x188, 0)
        run(16)
        assert r32(object_base + 0x1c4) == cfg_word(0x540), \
            "state 16 zero callback did not take the default clip"

        # --- state 17 -------------------------------------------------------
        # Clip end: +0x172 = 0, +0x170 = 1, +0x1a8 = 2, +0x1c4 = +0x1b2 = 0.
        reset_object()
        setup_config()
        set_count(REC0, 1)
        w16(object_base + 0x188, 0)
        w16(object_base + 0x17a, 0)
        w16(object_base + 0x194, 0x1111)
        w16(object_base + 0x178, 0x2222)
        w32(object_base + 0x1c4, 0xDEADBEEF)
        w16(object_base + 0x1b2, 0xBEEF)
        w8(object_base + 0x1a8, 0x55)
        run(17)
        assert r16(object_base + 0x172) == 0, "state 17 clip end +0x172 != 0"
        assert r16(object_base + 0x170) == 1, "state 17 clip end +0x170 != 1"
        assert r16(object_base + 0x194) == 0, "state 17 clip end +0x194 != 0"
        assert r16(object_base + 0x178) == 0, "state 17 clip end +0x178 != 0"
        assert r16(object_base + 0x17a) == 0, "state 17 clip end +0x17a != 0"
        assert r8(object_base + 0x1a8) == 2, "state 17 clip end +0x1a8 != 2"
        assert r32(object_base + 0x1c4) == 0, "state 17 wrote +0x1c4 != 0"
        assert r16(object_base + 0x1b2) == 0, "state 17 wrote +0x1b2 != 0"

        # Advance path keeps +0x172 and bumps +0x17a.
        reset_object()
        setup_config()
        set_count(REC0, 5)
        w16(object_base + 0x188, 0)
        w16(object_base + 0x17a, 0)
        w16(object_base + 0x172, 0xABCD)
        run(17)
        assert r16(object_base + 0x17a) == 1, "state 17 did not advance +0x17a"
        assert r16(object_base + 0x172) == 0xABCD, \
            "state 17 advanced past the clip end"
        assert r32(object_base + 0x1c4) == 0
        assert r16(object_base + 0x1b2) == 0

        # --- state 32 -------------------------------------------------------
        # Clip end: +0x172 = 0, +0x170 = 1, +0x1a8 = 2, +0x1c4 by +0x176.
        for f176, speed in ((0, 0x570), (1, 0x574), (2, 0x56c)):
            reset_object()
            setup_config()
            set_count(REC0, 1)
            w16(object_base + 0x176, f176)
            w16(object_base + 0x17a, 0)
            run(32)
            assert r16(object_base + 0x172) == 0, \
                f"state 32 +0x176={f176}: +0x172 != 0"
            assert r16(object_base + 0x170) == 1, \
                f"state 32 +0x176={f176}: +0x170 != 1"
            assert r8(object_base + 0x1a8) == 2, \
                f"state 32 +0x176={f176}: +0x1a8 != 2"
            assert r32(object_base + 0x1c4) == cfg_word(speed), \
                (f"state 32 +0x176={f176}: +0x1c4 = "
                 f"0x{r32(object_base + 0x1c4):08x}")

        # Advance path sets +0x1af = 4 and bumps +0x17a.
        reset_object()
        setup_config()
        set_count(REC0, 5)
        w16(object_base + 0x176, 0)
        w16(object_base + 0x17a, 0)
        w16(object_base + 0x172, 0xABCD)
        run(32)
        assert r16(object_base + 0x17a) == 1, "state 32 did not advance +0x17a"
        assert r8(object_base + 0x1af) == 4, "state 32 +0x1af != 4"
        assert r16(object_base + 0x172) == 0xABCD, \
            "state 32 advanced past the clip end"
        assert r32(object_base + 0x1c4) == cfg_word(0x570)

        # --- state 36 -------------------------------------------------------
        # Clip end -> state 31 with the +0x4e accumulator.
        reset_object()
        setup_config()
        set_count(REC0, 1)
        w32(config_base + 0x658, 0x10)
        w32(config_base + 0x660, 0x1000)
        w16(object_base + 0x176, 0)
        w16(object_base + 0x17e, 0)
        w16(object_base + 0x17a, 0)
        w16(object_base + 0x4e, 0x100)
        w16(object_base + 0x1a0, 0x9999)
        w8(object_base + 0x1a8, 0)
        w8(object_base + 0x1a9, 0)
        w16(object_base + 0x172, 0xABCD)
        run(36)
        assert r16(object_base + 0x172) == 31, "state 36 clip end +0x172 != 31"
        assert r16(object_base + 0x170) == 0, "state 36 clip end +0x170 != 0"
        assert r16(object_base + 0x17a) == 0, "state 36 clip end +0x17a != 0"
        assert r16(object_base + 0x17e) == 1, "state 36 clip end +0x17e != 1"
        assert r16(object_base + 0x1a0) == 0, "state 36 clip end +0x1a0 != 0"
        assert r8(object_base + 0x1a8) == 1, "state 36 clip end +0x1a8 != 1"
        assert r8(object_base + 0x1a9) == 1, "state 36 clip end +0x1a9 != 1"
        assert r16(object_base + 0x4e) == 0x110, \
            f"state 36 +0x4e = 0x{r16(object_base + 0x4e):04x}"
        assert r32(object_base + 0x1c4) == cfg_word(0x570), \
            "state 36 default +0x1c4"

        # Advance path keeps +0x172.
        reset_object()
        setup_config()
        set_count(REC0, 5)
        w16(object_base + 0x176, 0)
        w16(object_base + 0x17e, 0)
        w16(object_base + 0x17a, 0)
        w16(object_base + 0x172, 0xABCD)
        run(36)
        assert r16(object_base + 0x17a) == 1, "state 36 did not advance +0x17a"
        assert r16(object_base + 0x172) == 0xABCD, \
            "state 36 advanced past the clip end"

        # Weapon sentinel gate sets +0x174.
        reset_object()
        setup_config()
        set_count(REC0, 5)
        w16(object_base + 0x13a, 0xFF)
        w8(object_base + 0x1df, 1)
        w16(object_base + 0x174, 0)
        run(36)
        assert r16(object_base + 0x174) == 3, \
            f"state 36 weapon gate +0x174 = {r16(object_base + 0x174)}"

        # +0x1c4 by +0x176.
        for f176, speed in ((0, 0x570), (1, 0x574), (2, 0x56c)):
            reset_object()
            setup_config()
            set_count(REC0, 5)
            w16(object_base + 0x176, f176)
            w16(object_base + 0x17e, 0)
            w16(object_base + 0x17a, 0)
            run(36)
            assert r32(object_base + 0x1c4) == cfg_word(speed), \
                (f"state 36 +0x176={f176}: +0x1c4 = "
                 f"0x{r32(object_base + 0x1c4):08x}")

    # --- source constants ---------------------------------------------------
    text = SOURCE.read_text(encoding="utf-8")
    for fragment in (
            "recovered_state_locomotion_0_run",
            "recovered_state_locomotion_1_run",
            "recovered_state_locomotion_15_run",
            "recovered_state_locomotion_16_run",
            "recovered_state_locomotion_17_run",
            "recovered_state_locomotion_32_run",
            "recovered_state_locomotion_36_run",
            "RECOVERED_STATE_LOCOMOTION_CONFIG_OFFSET 0x6cU",
            "0x3a8U", "0x3b0U", "0x3b8U", "0x3c0U", "0x3c8U",
            "0x3acU", "0x3b4U", "0x3bcU", "0x3c4U",
            "0x534U", "0x538U", "0x530U",
            "0x53cU", "0x540U", "0x544U",
            "0x554U", "0x558U", "0x55cU", "0x560U", "0x564U", "0x568U",
            "0x56cU", "0x570U", "0x574U", "0x658U", "0x660U",
            "0x98U", "0x9cU", "0xa0U", "0xa4U", "0xa8U", "0xacU",
            "0xb0U", "0xb4U", "0x70U", "0x74U",
            "0xb8U", "0xbcU", "0xd8U", "0xdcU",
            "0x108U", "0x10cU", "0x368U", "0x36cU",
            "0x51ab08", "0x51ab0c", "0x51ab10", "0x51ab12"):
        if fragment not in text:
            raise AssertionError(
                f"state-locomotion-arms model missing {fragment}")

    # --- listing evidence ---------------------------------------------------
    listing = LISTING.read_text(encoding="utf-8")

    def block(start, end):
        return listing[listing.index(start):listing.index(end)]

    state0 = block("   2f580:", "   2f930:")
    state1 = block("   2f930:", "   2fa20:")
    state15 = block("   2fa20:", "   2fb20:")
    state16 = block("   2fb20:", "   2fd50:")
    state17 = block("   2fd50:", "   2fe30:")
    state32 = block("   30c20:", "   30d40:")
    state36 = block("   31210:", "   313e0:")

    evidence = {
        0: (state0, (
            "stos\tg14,0x186(g0)", "ldos\t0x170(g0),g4",
            "ld\t0x3a8(g5),g4", "ld\t0x3b0(g5),g4",
            "ld\t0x3c0(g5),g4", "ld\t0x3b8(g5),g4",
            "shrdi\t1,g4,g4", "stos\tg5,0x2e(g0)",
            "ldos\t0x10e(g0),g4", "cmpibge\t0,g4,0x2f6ec",
            "st\tg5,0x51ab08", "st\tg6,0x51ab0c",
            "ld\t0x9c(g4),g5", "ld\t0x98(g4),g6",
            "ld\t0xac(g4),g5", "ld\t0xa8(g4),g6",
            "ld\t0xa4(g5),g6", "ld\t0xa0(g5),g7",
            "ld\t0xb4(g5),g6", "ld\t0xb0(g5),g7",
            "ld\t0x70(g4),g6", "ld\t0x74(g4),g7",
            "ldob\t0x1db(g0),g4", "ldob\t0x1dc(g0),g4",
            "stos\tg14,0x1b2(r4)")),
        1: (state1, (
            "ld\t0x3c8(g4),g1", "callx\t(g1)",
            "ldos\t0x17c(r4),g4", "bne\t0x2fa14",
            "stos\tg14,0x172(r4)", "stos\tg2,0x170(r4)",
            "ldob\t0x139(r4),g4", "ldos\t0x102(r4),g4",
            "bbs\t15,g4,0x2fa14", "stos\tg2,0x172(r4)",
            "lda\t0xefff(g5),g4", "and\tg6,g4,g4",
            "stos\tg5,0x186(r4)", "lda\t0xdfff(g5),g4",
            "cmpobg\tg4,g2,0x2f9ec", "lda\t0xa000(g5),g4",
            "stos\tg4,0x188(r4)")),
        15: (state15, (
            "lda\t0x2fb10,g14", "ldos\t0x188(g0),g4",
            "ld\t0x7c(g5)[g4],g7", "ld\t0x78(g5)[g4],g6",
            "st\tg7,0x51ab08", "st\tg6,0x51ab0c",
            "cmpi\tg5,g4", "bl\t0x2fab8",
            "mov\t16,g1", "stos\tg1,0x172(g0)",
            "ld\t0x534(g5),g5", "ld\t0x538(g5),g5",
            "ld\t0x530(g5),g5", "st\tg5,0x1c4(g0)",
            "stos\tg14,0x1b2(g0)")),
        16: (state16, (
            "ldos\t0x170(g0),g4", "ld\t0x3ac(g5),g4",
            "ld\t0x3b4(g5),g4", "ld\t0x3c4(g5),g4",
            "ld\t0x3bc(g5),g4", "ld\t0x558(g4),g4",
            "ld\t0x55c(g4),g4", "ld\t0x554(g4),g4",
            "ld\t0x564(g4),g4", "ld\t0x568(g4),g4",
            "ld\t0x560(g4),g4", "ld\t0x540(g4),g4",
            "ld\t0x544(g4),g4", "ld\t0x53c(g4),g4",
            "ld\t0xbc(g5)[g4],g6", "ld\t0xb8(g5)[g4],g7",
            "st\tg6,0x51ab08", "st\tg7,0x51ab0c",
            "bl\t0x2fce0", "stos\tg14,0x1b2(r4)")),
        17: (state17, (
            "lda\t0x2fe28,g14", "ld\t0xdc(g5)[g4],g7",
            "ld\t0xd8(g5)[g4],g6", "st\tg7,0x51ab08",
            "st\tg6,0x51ab0c", "bl\t0x2fe00",
            "stos\tg14,0x172(g0)", "stos\tg1,0x170(g0)",
            "stos\tg14,0x194(g0)", "mov\t2,g1",
            "stob\tg1,0x1a8(g0)", "st\tg14,0x1c4(g0)",
            "stos\tg14,0x1b2(g0)")),
        32: (state32, (
            "lda\t0x30d38,g14", "ldos\t0x176(g0),g4",
            "ld\t0x108(g5)[g4],g6", "ld\t0x10c(g5)[g4],g7",
            "st\tg6,0x51ab0c", "st\tg7,0x51ab08",
            "bl\t0x30cd4", "mov\t4,g1",
            "stob\tg1,0x1af(g0)", "stos\tg14,0x172(g0)",
            "mov\t2,g1", "stob\tg1,0x1a8(g0)",
            "ld\t0x570(g5),g5", "ld\t0x574(g5),g5",
            "ld\t0x56c(g5),g5")),
        36: (state36, (
            "lda\t0x313d4,g14", "stos\tg14,0x170(g0)",
            "ld\t0x368(g7)[g4],g6", "ld\t0x36c(g7)[g4],g5",
            "st\tg6,0x51ab0c", "st\tg5,0x51ab08",
            "ld\t0x570(g7),g7", "ld\t0x574(g7),g7",
            "ld\t0x56c(g7),g7", "ldob\t0x13a(g0),g4",
            "ldob\t0x138(g0),g4", "ldob\t0x139(g0),g4",
            "ldob\t0x13c(g0),g4", "mov\t3,g1",
            "mov\t16,g1", "stos\tg1,0x174(g0)",
            "cmpibl\tg5,g4,0x313b4", "mov\t31,g1",
            "stos\tg1,0x172(g0)", "stob\tg1,0x1a8(g0)",
            "stob\tg1,0x1a9(g0)", "ld\t0x658(g7),g5",
            "ld\t0x660(g7),g6", "stos\tg4,0x4e(g0)")),
    }
    for state, (state_block, fragments) in evidence.items():
        for fragment in fragments:
            if fragment not in state_block:
                raise AssertionError(
                    f"state {state} listing evidence missing: {fragment}")

    print("PASS: recovered state locomotion arms 0/1/15/16/17/32/36")


if __name__ == "__main__":
    main()
