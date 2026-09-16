#!/usr/bin/env python3
"""Validate the runnable velocity-producer driver at i960 0xde990-0xdf058.

The runnable object touches fixed absolute MMIO (0x884000) and board globals
(0x503b00, ...), so _run is never invoked here.  Only the pure integer
scale/flip helpers and the pure select/apply pair are exercised, together with
the listing evidence for the 0xde990-0xdf058 block.
"""

import ctypes
import pathlib
import struct
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_gameplay_velocity_de990_run.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

PLAYER = 0
CPU = 1

RULE_DOUBLED_NEGATED_OTHER = 0
RULE_SIGNED = 1
RULE_DOUBLED_SELF = 2

THR_70 = 0x428C0000
THR_30 = 0x41F00000
THR_DEFAULT = 0x41266666


class Plan(ctypes.Structure):
    _fields_ = [
        ("clear_player", ctypes.c_uint32),
        ("clear_cpu", ctypes.c_uint32),
        ("self_object", ctypes.c_uint32),
        ("other_object", ctypes.c_uint32),
        ("threshold_bits", ctypes.c_uint32),
        ("rule", ctypes.c_uint32),
    ]


class Velocity(ctypes.Structure):
    _fields_ = [
        ("player_written", ctypes.c_uint32),
        ("cpu_written", ctypes.c_uint32),
        ("player", ctypes.c_uint32 * 2),
        ("cpu", ctypes.c_uint32 * 2),
    ]


def bits(value):
    return struct.unpack("<I", struct.pack("<f", value))[0]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "gameplay-velocity-de990-run.so"
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
             "-O2", str(SOURCE), "-o", str(library)],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))

        scale2x = recovered.recovered_gameplay_velocity_de990_scale2x
        scale2x.argtypes = [ctypes.c_uint32]
        scale2x.restype = ctypes.c_uint32

        flip31 = recovered.recovered_gameplay_velocity_de990_flip31
        flip31.argtypes = [ctypes.c_uint32]
        flip31.restype = ctypes.c_uint32

        select = recovered.recovered_gameplay_velocity_de990_run_select
        select.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
            ctypes.c_uint32, ctypes.POINTER(Plan),
        ]
        select.restype = None

        apply = recovered.recovered_gameplay_velocity_de990_run_apply
        apply.argtypes = [
            ctypes.POINTER(Plan), ctypes.c_uint32, ctypes.c_uint32,
            ctypes.c_uint32, ctypes.POINTER(Velocity),
        ]
        apply.restype = ctypes.c_uint32

        # --- integer-only doubling (exponent+1) -----------------------------
        assert scale2x(bits(2.5)) == bits(5.0)
        assert scale2x(bits(-1.5)) == bits(-3.0)
        assert scale2x(bits(1.0)) == bits(2.0)
        assert scale2x(0x00000000) == 0x00000000
        assert scale2x(0x80000000) == 0x80000000
        # Denormals are left alone rather than normalized.
        assert scale2x(0x00000001) == 0x00000001
        # exponent 0xfe overflows to infinity, sign preserved.
        assert scale2x(0x7F000000) == 0x7F800000
        assert scale2x(0xFF000000) == 0xFF800000
        # infinity and NaN are returned unchanged.
        assert scale2x(0x7F800000) == 0x7F800000
        assert scale2x(0xFF800000) == 0xFF800000
        assert scale2x(0x7FC00000) == 0x7FC00000

        # --- notbit 31 ------------------------------------------------------
        assert flip31(0x80000000) == 0x00000000
        assert flip31(0x00000000) == 0x80000000
        assert flip31(0x40400000) == 0xC0400000
        # The listing's doubled-negated-other arm composes flip then double.
        assert scale2x(flip31(bits(-3.0))) == bits(6.0)
        assert scale2x(flip31(bits(3.0))) == bits(-6.0)

        def choose(stage, state, mode_primary, mode_secondary):
            plan = Plan()
            select(stage, state, mode_primary, mode_secondary,
                   ctypes.byref(plan))
            return plan

        def plan_tuple(plan):
            return (plan.clear_player, plan.clear_cpu, plan.self_object,
                    plan.other_object, plan.threshold_bits, plan.rule)

        # --- mode/variant selection -----------------------------------------
        # 0x504134 == 9: self=CPU, other=player, 70.0, double-negate the other.
        assert plan_tuple(choose(4, 0, 9, 0)) == \
            (1, 1, CPU, PLAYER, THR_70, RULE_DOUBLED_NEGATED_OTHER)
        # 0x504134 == 8: identical shape at 30.0.
        assert plan_tuple(choose(0, 1, 8, 0)) == \
            (1, 1, CPU, PLAYER, THR_30, RULE_DOUBLED_NEGATED_OTHER)
        # 0x503b34 == 9: roles swap, output is the CPU object, 70.0.
        assert plan_tuple(choose(4, 0, 0, 9)) == \
            (1, 1, PLAYER, CPU, THR_70, RULE_DOUBLED_NEGATED_OTHER)
        # 0x503b34 == 8: same at 30.0.
        assert plan_tuple(choose(0, 1, 0, 8)) == \
            (1, 1, PLAYER, CPU, THR_30, RULE_DOUBLED_NEGATED_OTHER)
        # Gate default: both modes unrecognized, 10.4 signed split.
        assert plan_tuple(choose(4, 0, 7, 7)) == \
            (1, 1, CPU, PLAYER, THR_DEFAULT, RULE_SIGNED)
        # state == 3 fallback: CPU is NOT cleared and self doubles.
        assert plan_tuple(choose(0, 3, 9, 9)) == \
            (1, 0, PLAYER, CPU, THR_DEFAULT, RULE_DOUBLED_SELF)
        # Any other fallback state: CPU cleared, signed split.
        assert plan_tuple(choose(0, 5, 0, 0)) == \
            (1, 1, PLAYER, CPU, THR_DEFAULT, RULE_SIGNED)
        # The 16-bit stage/state operands are zero-extended before the compare.
        assert plan_tuple(choose(0x10004, 0x00000, 9, 0)) == \
            (1, 1, CPU, PLAYER, THR_70, RULE_DOUBLED_NEGATED_OTHER)
        assert plan_tuple(choose(0x00000, 0x10001, 0, 0)) == \
            (1, 1, CPU, PLAYER, THR_DEFAULT, RULE_SIGNED)

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

    # --- listing evidence ---------------------------------------------------
    listing = LISTING.read_text(encoding="utf-8")
    block = listing[listing.index("   de990:"):listing.index("   df058:")]
    for evidence in (
            "0x428c0000", "0x41f00000", "0x41266666",
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

    print("recovered gameplay velocity de990 runnable: ok")


if __name__ == "__main__":
    main()
