#!/usr/bin/env python3
"""Host test for the recovered i960 315-5649 input service.

Compiles von/i960/recovered_input_service_run.c with
    cc -std=c11 -Wall -Wextra -Werror -shared -fPIC
and drives the pure IN1/IN2 -> (command code, MA, MB) helper plus the run core
against local object and MA/MB buffers. The absolute 0x01c00000 port read lives
in a thin wrapper and is intentionally not exercised on the host.
"""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_input_service_run.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"
PORTS = ROOT / "mame/src/mame/sega/model2.cpp"

CC = ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC"]

OBJ_SIZE = 0x200

BIT_SHOT = 0x01
BIT_DASH = 0x02
BIT_DOWN = 0x10
BIT_UP = 0x20
BIT_RIGHT = 0x40
BIT_LEFT = 0x80

TABLE = [
    0x00ff, 0x0004, 0x0000, 0x00ff, 0x0006, 0x0005, 0x0007, 0x00ff,
    0x0002, 0x0003, 0x0001, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff,
]


def axis(logical, positive, negative):
    return (1 if logical & positive else 0) - (1 if logical & negative else 0)


def derive_ref(in1, in2):
    """Independent model of the sum/difference + 0x3d70/0x3da0 nibble lookup."""
    left = (~in1) & 0xff
    right = (~in2) & 0xff
    buttons = (left | right) & (BIT_SHOT | BIT_DASH)
    lz = axis(left, BIT_UP, BIT_DOWN)
    lx = axis(left, BIT_RIGHT, BIT_LEFT)
    rz = axis(right, BIT_UP, BIT_DOWN)
    rx = axis(right, BIT_RIGHT, BIT_LEFT)
    ma = buttons
    mb = buttons
    sum_z, sum_x = lz + rz, lx + rx
    diff_z, diff_x = lz - rz, lx - rx
    if sum_z > 0:
        ma |= BIT_UP
    elif sum_z < 0:
        ma |= BIT_DOWN
    if sum_x > 0:
        ma |= BIT_RIGHT
    elif sum_x < 0:
        ma |= BIT_LEFT
    if diff_z > 0:
        mb |= BIT_UP
    elif diff_z < 0:
        mb |= BIT_DOWN
    if diff_x > 0:
        mb |= BIT_RIGHT
    elif diff_x < 0:
        mb |= BIT_LEFT
    code = ((TABLE[(ma >> 4) & 0x0f] << 8) | TABLE[(mb >> 4) & 0x0f]) & 0xffff
    return code, ma, mb


def sibling_redecode(source_word):
    """0x250f4-0x2515c: table[(word>>12)&15]<<8 | table[(word>>20)&15]."""
    hi = TABLE[(source_word >> 12) & 0x0f]
    lo = TABLE[(source_word >> 20) & 0x0f]
    return ((hi << 8) | lo) & 0xffff


def sign_extend_byte(value):
    value &= 0xff
    return value - 256 if value >= 128 else value


class Derived(ctypes.Structure):
    _fields_ = [
        ("command_code", ctypes.c_uint32),
        ("ma", ctypes.c_uint32),
        ("mb", ctypes.c_uint32),
    ]


def read_half(obj, offset):
    return int.from_bytes(bytes(obj[offset:offset + 2]), "little")


def read_word(obj, offset):
    return int.from_bytes(bytes(obj[offset:offset + 4]), "little")


def main():
    # Active-low raw device bytes: clear the pressed bit from 0xff.
    holds = {
        "both_forward": ((~BIT_UP) & 0xff, (~BIT_UP) & 0xff),
        "both_back": ((~BIT_DOWN) & 0xff, (~BIT_DOWN) & 0xff),
        "strafe_right": ((~BIT_RIGHT) & 0xff, (~BIT_RIGHT) & 0xff),
        "strafe_left": ((~BIT_LEFT) & 0xff, (~BIT_LEFT) & 0xff),
        "sticks_together_guard": ((~BIT_RIGHT) & 0xff, (~BIT_LEFT) & 0xff),
        "sticks_apart_jump": ((~BIT_LEFT) & 0xff, (~BIT_RIGHT) & 0xff),
        "forward_dash": ((~(BIT_UP | BIT_DASH)) & 0xff,
                         (~(BIT_UP | BIT_DASH)) & 0xff),
        "single_left_up": ((~BIT_UP) & 0xff, 0xff),
        "single_right_up": (0xff, (~BIT_UP) & 0xff),
        "shot_alone": ((~BIT_SHOT) & 0xff, 0xff),
        "neutral": (0xff, 0xff),
    }

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "input-service.so"
        subprocess.run(CC + [str(SOURCE), "-o", str(library)], check=True)
        recovered = ctypes.CDLL(str(library))

        derive = recovered.recovered_input_service_derive
        derive.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                           ctypes.POINTER(Derived)]
        derive.restype = None

        run_core = recovered.recovered_input_service_run_core
        run_core.argtypes = [ctypes.POINTER(ctypes.c_ubyte),
                             ctypes.c_uint32, ctypes.c_uint32,
                             ctypes.POINTER(ctypes.c_uint32),
                             ctypes.POINTER(ctypes.c_uint32)]
        run_core.restype = None

        for name, (in1, in2) in holds.items():
            expected = derive_ref(in1, in2)
            out = Derived()
            derive(in1, in2, ctypes.byref(out))
            got = (out.command_code, out.ma, out.mb)
            assert got == expected, (name, hex(in1), hex(in2), got, expected)
            assert out.command_code <= 0xffff, name

            obj = (ctypes.c_ubyte * OBJ_SIZE)()
            ma = ctypes.c_uint32(0)
            mb = ctypes.c_uint32(0)
            run_core(obj, in1, in2, ctypes.byref(ma), ctypes.byref(mb))

            assert read_half(obj, 0x108) == expected[0], name
            assert ma.value == sign_extend_byte(expected[1]) & 0xffffffff, name
            assert mb.value == sign_extend_byte(expected[2]) & 0xffffffff, name
            source = read_word(obj, 0xec)
            assert read_word(obj, 0xf0) == expected[2], name
            # Re-running the sibling decoder on object+0xec must reproduce
            # object+0x108 exactly.
            assert sibling_redecode(source) == read_half(obj, 0x108), name

        def derived_of(name):
            return derive_ref(*holds[name])

        # Explicit gesture expectations (raw -> logical -> MA/MB).
        assert derived_of("both_forward") == (0x00ff, 0x20, 0x00)
        assert derived_of("both_back") == (0x04ff, 0x10, 0x00)
        assert derived_of("strafe_right") == (0x06ff, 0x40, 0x00)
        assert derived_of("strafe_left") == (0x02ff, 0x80, 0x00)
        assert derived_of("sticks_together_guard") == (0xff06, 0x00, 0x40)
        assert derived_of("sticks_apart_jump") == (0xff02, 0x00, 0x80)
        assert derived_of("forward_dash") == (0x00ff, 0x22, 0x02)
        assert derived_of("single_left_up") == (0x0000, 0x20, 0x20)
        assert derived_of("single_right_up") == (0x0004, 0x20, 0x10)
        assert derived_of("shot_alone") == (0xffff, 0x01, 0x01)
        assert derived_of("neutral") == (0xffff, 0x00, 0x00)

        # The recovered tables 0x3d70/0x3da0 select the 0xff no-command lane
        # for neutral and the 0xff0X family for pure twist gestures.
        assert derived_of("sticks_together_guard")[0] & 0xff00 == 0xff00
        assert derived_of("sticks_apart_jump")[0] & 0xff00 == 0xff00

        # --- listing evidence: sibling copy + nibble command decode ---------
        listing = LISTING.read_text(encoding="utf-8")
        for evidence in (
                "ld\t0x50249c,g4", "st\tg4,(r14)", "ld\t0x5024a4,g4",
                "st\tg4,0xf0(g0)", "ldos\t0x108(g0),g4",
                "ld\t0x3d90,g5", "ld\t0x3dc0,g6",
                "ldos\t0x3d70[g4*2],g5", "ldos\t0x3da0[g4*2],g4",
                "shro\tg5,g4,g4", "and\t15,g4,g4", "shlo\t8,g5,g5",
                "or\tg4,g5,g5", "stos\tg5,0x108(g0)"):
            if evidence not in listing:
                raise AssertionError(
                    f"0x25040 nibble-decode listing evidence missing: "
                    f"{evidence!r}")

        # --- listing evidence: 0x2da0 reads the 315-5649 port window -------
        for evidence in (
                "lda\t0x1c00000,g1", "ldos\t0x2(g1),g7",
                "ldos\t0x4(g1),g5", "ldos\t0x6(g1),g4"):
            if evidence not in listing:
                raise AssertionError(
                    f"0x2da0 controller-read listing evidence missing: "
                    f"{evidence!r}")

        # --- listing evidence: the table data itself -----------------------
        for evidence in ("    3d70:", "    3d90:", "    3da0:", "    3dc0:"):
            if evidence not in listing:
                raise AssertionError(
                    f"nibble table/source listing evidence missing: "
                    f"{evidence!r}")

        # --- port layout evidence ------------------------------------------
        ports = PORTS.read_text(encoding="utf-8")
        for evidence in (
                'map(0x01c00000, 0x01c0001f).rw("io"',
                'io.in_pc_callback().set_ioport("IN1");',
                'io.in_pd_callback().set_ioport("IN2");',
                'PORT_BIT(0x01, IP_ACTIVE_LOW, IPT_BUTTON1) '
                'PORT_NAME("P1 Left Shot")',
                'PORT_BIT(0x02, IP_ACTIVE_LOW, IPT_BUTTON2) '
                'PORT_NAME("P1 Left Dash")',
                "PORT_BIT(0x20, IP_ACTIVE_LOW, IPT_JOYSTICKLEFT_UP)",
                "PORT_BIT(0x80, IP_ACTIVE_LOW, IPT_JOYSTICKLEFT_LEFT)",
                'PORT_BIT(0x01, IP_ACTIVE_LOW, IPT_BUTTON3) '
                'PORT_NAME("P1 Right Shot")',
                "PORT_BIT(0x80, IP_ACTIVE_LOW, IPT_JOYSTICKRIGHT_LEFT)"):
            if evidence not in ports:
                raise AssertionError(f"model2.cpp port-layout evidence missing: "
                                     f"{evidence!r}")

    print("PASS: recovered 315-5649 input service (0x2da0 + 0x250f4 nibble path)")


if __name__ == "__main__":
    main()
