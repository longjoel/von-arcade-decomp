#!/usr/bin/env python3
"""Validate the bounded velocity-producer slice at i960 0xde990-0xdf058."""

import ctypes
import pathlib
import struct
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_gameplay_velocity_de990.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

PLAYER = 0
CPU = 1

TRANSFORM_NONE = 0
TRANSFORM_DOUBLED_NEGATED_OTHER = 1
TRANSFORM_SIGNED = 2
TRANSFORM_DOUBLED_SELF = 3

SEL_504134_MODE9 = 0
SEL_504134_MODE8 = 1
SEL_503B34_MODE9 = 2
SEL_503B34_MODE8 = 3
SEL_GATE_DEFAULT = 4
SEL_STATE3_DOUBLED = 5
SEL_STATE_DEFAULT_SIGNED = 6

THR_70 = 0x428C0000
THR_30 = 0x41F00000
THR_DEFAULT = 0x41266666

SERVICE_SELF = 38
SERVICE_OTHER = 39


class Plan(ctypes.Structure):
    _fields_ = [
        ("clear_player", ctypes.c_uint32),
        ("clear_cpu", ctypes.c_uint32),
        ("self_object", ctypes.c_uint32),
        ("other_object", ctypes.c_uint32),
        ("threshold_bits", ctypes.c_uint32),
        ("transform", ctypes.c_uint32),
        ("selection", ctypes.c_uint32),
    ]


class Velocity(ctypes.Structure):
    _fields_ = [
        ("player_written", ctypes.c_uint32),
        ("cpu_written", ctypes.c_uint32),
        ("player", ctypes.c_uint32 * 2),
        ("cpu", ctypes.c_uint32 * 2),
    ]


class Packet(ctypes.Structure):
    _fields_ = [
        ("service_self", ctypes.c_uint32),
        ("service_other", ctypes.c_uint32),
        ("word_count", ctypes.c_uint32),
        ("words", ctypes.c_uint32 * 10),
    ]


def bits(value):
    return struct.unpack("<I", struct.pack("<f", value))[0]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "gameplay-velocity-de990.so"
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
             "-O2", str(SOURCE), "-o", str(library)],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))

        select = recovered.recovered_gameplay_velocity_de990_select
        select.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
            ctypes.c_uint32, ctypes.POINTER(Plan),
        ]
        select.restype = None

        apply = recovered.recovered_gameplay_velocity_de990_apply
        apply.argtypes = [
            ctypes.POINTER(Plan), ctypes.c_uint32, ctypes.c_uint32,
            ctypes.c_uint32, ctypes.POINTER(Velocity),
        ]
        apply.restype = ctypes.c_uint32

        build_packet = recovered.recovered_gameplay_velocity_de990_build_packet
        build_packet.argtypes = [
            ctypes.POINTER(Plan), ctypes.c_uint32 * 3, ctypes.c_uint32 * 3,
            ctypes.POINTER(Packet),
        ]
        build_packet.restype = None

        toggle_sign = recovered.recovered_gameplay_velocity_de990_toggle_sign
        toggle_sign.argtypes = [ctypes.c_uint32]
        toggle_sign.restype = ctypes.c_uint32

        double = recovered.recovered_gameplay_velocity_de990_double
        double.argtypes = [ctypes.c_uint32]
        double.restype = ctypes.c_uint32

        def choose(stage, state, mode_primary, mode_secondary):
            plan = Plan()
            select(stage, state, mode_primary, mode_secondary,
                   ctypes.byref(plan))
            return plan

        def plan_tuple(plan):
            return (plan.clear_player, plan.clear_cpu, plan.self_object,
                    plan.other_object, plan.threshold_bits, plan.transform,
                    plan.selection)

        # --- mode/variant selection -----------------------------------------
        # 0x504134 == 9: self=CPU, other=player, 70.0, double-negate the other.
        assert plan_tuple(choose(4, 0, 9, 0)) == \
            (1, 1, CPU, PLAYER, THR_70, TRANSFORM_DOUBLED_NEGATED_OTHER,
             SEL_504134_MODE9)
        # 0x504134 == 8: identical shape at 30.0.
        assert plan_tuple(choose(0, 1, 8, 0)) == \
            (1, 1, CPU, PLAYER, THR_30, TRANSFORM_DOUBLED_NEGATED_OTHER,
             SEL_504134_MODE8)
        # 0x503b34 == 9: roles swap, output is the CPU object, 70.0.
        assert plan_tuple(choose(4, 0, 0, 9)) == \
            (1, 1, PLAYER, CPU, THR_70, TRANSFORM_DOUBLED_NEGATED_OTHER,
             SEL_503B34_MODE9)
        # 0x503b34 == 8: same at 30.0.
        assert plan_tuple(choose(0, 1, 0, 8)) == \
            (1, 1, PLAYER, CPU, THR_30, TRANSFORM_DOUBLED_NEGATED_OTHER,
             SEL_503B34_MODE8)
        # Gate default: both modes unrecognized, 10.4 signed split.
        assert plan_tuple(choose(4, 0, 7, 7)) == \
            (1, 1, CPU, PLAYER, THR_DEFAULT, TRANSFORM_SIGNED,
             SEL_GATE_DEFAULT)
        # state == 3 fallback: CPU is NOT cleared and self doubles.
        assert plan_tuple(choose(0, 3, 9, 9)) == \
            (1, 0, PLAYER, CPU, THR_DEFAULT, TRANSFORM_DOUBLED_SELF,
             SEL_STATE3_DOUBLED)
        # Any other fallback state: CPU cleared, signed split.
        assert plan_tuple(choose(0, 5, 0, 0)) == \
            (1, 1, PLAYER, CPU, THR_DEFAULT, TRANSFORM_SIGNED,
             SEL_STATE_DEFAULT_SIGNED)
        # The 16-bit stage/state operands are zero-extended before the compare.
        assert plan_tuple(choose(0x10004, 0x00000, 9, 0)) == \
            (1, 1, CPU, PLAYER, THR_70, TRANSFORM_DOUBLED_NEGATED_OTHER,
             SEL_504134_MODE9)
        assert plan_tuple(choose(0x00000, 0x10001, 0, 0)) == \
            (1, 1, CPU, PLAYER, THR_DEFAULT, TRANSFORM_SIGNED,
             SEL_GATE_DEFAULT)

        # --- lane helpers ---------------------------------------------------
        assert toggle_sign(0x80000000) == 0x00000000
        assert toggle_sign(0x40400000) == 0xC0400000
        # Negative input: notbit clears the sign, so double() yields 2*|r|.
        assert double(toggle_sign(bits(-3.0))) == bits(6.0)
        assert double(bits(2.5)) == bits(5.0)
        assert double(bits(-1.5)) == bits(-3.0)

        # --- doubled-negated-other velocity output --------------------------
        plan = choose(4, 0, 9, 0)
        velocity = Velocity()
        assert apply(ctypes.byref(plan), bits(-3.0), bits(-4.0), 1,
                     ctypes.byref(velocity)) == 1
        # Output object is the player and the magnitude is doubled.
        assert (velocity.player_written, velocity.cpu_written) == (1, 0)
        assert list(velocity.player) == [bits(6.0), bits(8.0)]
        assert list(velocity.cpu) == [0, 0]
        # A positive response makes the sign toggle explicit (not abs).
        assert apply(ctypes.byref(plan), bits(3.0), bits(4.0), 1,
                     ctypes.byref(velocity)) == 1
        assert list(velocity.player) == [bits(-6.0), bits(-8.0)]

        # The 0x503b34 mode-9 shape publishes the CPU object instead.
        plan = choose(4, 0, 0, 9)
        assert apply(ctypes.byref(plan), bits(-3.0), bits(-4.0), 1,
                     ctypes.byref(velocity)) == 1
        assert (velocity.player_written, velocity.cpu_written) == (0, 1)
        assert list(velocity.cpu) == [bits(6.0), bits(8.0)]

        # --- doubled-self velocity output (state 3) -------------------------
        plan = choose(0, 3, 9, 9)
        assert apply(ctypes.byref(plan), bits(2.5), bits(1.5), 1,
                     ctypes.byref(velocity)) == 1
        assert (velocity.player_written, velocity.cpu_written) == (1, 0)
        assert list(velocity.player) == [bits(5.0), bits(3.0)]

        # --- signed split ---------------------------------------------------
        # Gate default: self is the CPU, so the CPU keeps r and the player gets -r.
        plan = choose(4, 0, 7, 7)
        assert apply(ctypes.byref(plan), bits(2.0), bits(-4.0), 1,
                     ctypes.byref(velocity)) == 1
        assert (velocity.player_written, velocity.cpu_written) == (1, 1)
        assert list(velocity.cpu) == [bits(2.0), bits(-4.0)]
        assert list(velocity.player) == [bits(-2.0), bits(4.0)]
        # Fallback state: self is the player, so the roles invert.
        plan = choose(0, 5, 0, 0)
        assert apply(ctypes.byref(plan), bits(2.0), bits(-4.0), 1,
                     ctypes.byref(velocity)) == 1
        assert list(velocity.player) == [bits(2.0), bits(-4.0)]
        assert list(velocity.cpu) == [bits(-2.0), bits(4.0)]

        # --- r3 == 0 gate ---------------------------------------------------
        plan = choose(4, 0, 9, 0)
        assert apply(ctypes.byref(plan), bits(-3.0), bits(-4.0), 0,
                     ctypes.byref(velocity)) == 0
        assert (velocity.player_written, velocity.cpu_written) == (0, 0)
        assert list(velocity.player) == [0, 0]
        assert list(velocity.cpu) == [0, 0]

        # --- emitted service packet -----------------------------------------
        plan = choose(4, 0, 9, 0)
        self_position = (ctypes.c_uint32 * 3)(0x11, 0x22, 0x33)
        other_position = (ctypes.c_uint32 * 3)(0x44, 0x55, 0x66)
        packet = Packet()
        build_packet(ctypes.byref(plan), self_position, other_position,
                     ctypes.byref(packet))
        assert (packet.service_self, packet.service_other,
                packet.word_count) == (SERVICE_SELF, SERVICE_OTHER, 10)
        assert list(packet.words) == [
            SERVICE_SELF, 0x11, 0x22, 0x33, THR_70, 0,
            SERVICE_OTHER, 0x44, 0x55, 0x66,
        ]

        # --- listing evidence -----------------------------------------------
        listing = LISTING.read_text(encoding="utf-8")
        block = listing[listing.index("   de990:"):listing.index("   df058:")]
        for evidence in (
                "cmpibe\t4,g4,0xde9c0", "cmpibne\t1,g4,0xdee88",
                "cmpibe\t3,g4,0xdef7c", "cmpibne\t9,g4,0xdead4",
                "cmpibne\t8,g4,0xdebc8", "cmpibne\t9,g4,0xdecbc",
                "cmpibne\t8,g4,0xdedb0",
                "lda\t0x428c0000,r4", "lda\t0x41f00000,r4",
                "lda\t0x41266666,r4",
                "addo\t31,7,r5", "addo\t31,8,r5",
                "st\tr5,0x884000", "st\tg6,0x884000", "st\tg0,0x884000",
                "ldl\t0x5040d8,g6", "ldl\t0x503ad8,g0",
                "notbit\t31,g6,g4", "notbit\t31,g7,g4",
                "notbit\t31,g4,g6", "notbit\t31,g5,g6",
                "st\tg4,0x503c98", "st\tg4,0x504298"):
            if evidence not in block:
                raise AssertionError(
                    f"velocity listing evidence missing: {evidence}")

    print("recovered gameplay velocity de990 vectors: ok")


if __name__ == "__main__":
    main()
