#!/usr/bin/env python3
"""Validate the runnable i960 velocity accumulation block at 0x358ac.

The runnable object services SHARC opcodes 29/30 through the absolute 0x884000
FIFO, so _run is never invoked here.  Only the pure operand, clamp/scale and
add-real helpers are exercised, together with the listing evidence for the
0x358ac-0x35cd4 accumulation span (registered ledger range 0x358ac-0x35c28).
"""

import ctypes
import pathlib
import struct
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_velocity_accumulate_358ac.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


def bits(value):
    return struct.unpack("<I", struct.pack("<f", value))[0]


def float_of(word):
    return struct.unpack("<f", struct.pack("<I", word))[0]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "velocity-accumulate-358ac.so"
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared",
             "-fPIC", "-O2", str(SOURCE), "-o", str(library)],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))

        flip31 = recovered.recovered_velocity_accumulate_358ac_flip31
        flip31.argtypes = [ctypes.c_uint32]
        flip31.restype = ctypes.c_uint32

        add_lane = recovered.recovered_velocity_accumulate_358ac_add_lane
        add_lane.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        add_lane.restype = ctypes.c_uint32

        clamp = recovered.recovered_velocity_accumulate_358ac_clamp_speed
        clamp.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        clamp.restype = ctypes.c_uint32

        scale = recovered.recovered_velocity_accumulate_358ac_scale_speed
        scale.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        scale.restype = ctypes.c_uint32

        operands = recovered.recovered_velocity_accumulate_358ac_operands
        operands.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
        ]
        operands.restype = None

        apply = recovered.recovered_velocity_accumulate_358ac_apply
        apply.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
            ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
        ]
        apply.restype = None

        # --- notbit 31: the i960 sign-bit flip ------------------------------
        assert flip31(0x00000000) == 0x80000000
        assert flip31(0x80000000) == 0x00000000
        assert flip31(bits(2.0)) == bits(-2.0)
        assert flip31(bits(-2.0)) == bits(2.0)

        # --- addr add-real: the +0x1c8/+0x1cc accumulation ------------------
        assert add_lane(bits(10.0), bits(3.0)) == bits(13.0)
        assert add_lane(bits(10.0), bits(-3.0)) == bits(7.0)
        assert add_lane(bits(0.5), bits(0.25)) == bits(0.75)
        # i960 addition is commutative, so the listing operand order is moot.
        assert add_lane(bits(3.0), bits(10.0)) == add_lane(bits(10.0), bits(3.0))

        # --- +0x1c4 clamp to +0x7c (cmpr/ble) -------------------------------
        assert clamp(bits(5.0), bits(2.0)) == bits(2.0)
        assert clamp(bits(1.0), bits(2.0)) == bits(1.0)
        assert clamp(bits(2.0), bits(2.0)) == bits(2.0)
        assert clamp(bits(-5.0), bits(2.0)) == bits(-5.0)
        # cmp_d clears the condition bits for an unordered compare, so a NaN
        # speed or limit is clamped rather than passed through.
        assert clamp(0x7FC00000, bits(2.0)) == bits(2.0)
        assert clamp(bits(2.0), 0x7FC00000) == 0x7FC00000

        # --- +0x7c < 70.0 speed scaling (cmprl/bge) -------------------------
        # 10 * (20 + 130) / 200 = 7.5
        assert scale(bits(10.0), bits(20.0)) == bits(7.5)
        # 100 * (30 + 130) / 200 = 80.0
        assert scale(bits(100.0), bits(30.0)) == bits(80.0)
        # limit >= 70.0 skips the whole arm and returns the original bits.
        assert scale(bits(10.0), bits(70.0)) == bits(10.0)
        assert scale(bits(10.0), bits(90.0)) == bits(10.0)

        # --- operand computation: (angle, multiplier) --------------------
        a29 = ctypes.c_uint32()
        m29 = ctypes.c_uint32()
        a30 = ctypes.c_uint32()
        m30 = ctypes.c_uint32()
        operands(0x1234, bits(2.0), ctypes.byref(a29), ctypes.byref(m29),
                 ctypes.byref(a30), ctypes.byref(m30))
        assert a29.value == 0x1234
        assert m29.value == bits(-2.0)
        assert a30.value == 0x1234
        assert m30.value == bits(2.0)
        # The facing halfword is masked, so the high bits are ignored.
        operands(0xFFFFABCD, bits(1.0), ctypes.byref(a29), ctypes.byref(m29),
                 ctypes.byref(a30), ctypes.byref(m30))
        assert a29.value == 0xABCD
        assert a30.value == 0xABCD

        # --- response lane mapping: 29 -> x, 30 -> z ------------------------
        out_x = ctypes.c_uint32()
        out_z = ctypes.c_uint32()
        apply(bits(10.0), bits(20.0), bits(3.0), bits(-5.0),
              ctypes.byref(out_x), ctypes.byref(out_z))
        assert float_of(out_x.value) == 13.0
        assert float_of(out_z.value) == 15.0
        # Swapping the responses swaps the lanes.
        apply(bits(10.0), bits(20.0), bits(-5.0), bits(3.0),
              ctypes.byref(out_x), ctypes.byref(out_z))
        assert float_of(out_x.value) == 5.0
        assert float_of(out_z.value) == 23.0

    # --- source constants ---------------------------------------------------
    text = SOURCE.read_text(encoding="utf-8")
    for fragment in (
            "0x00884000U", "0x0051ab14U", "0x80000000U",
            "RECOVERED_VELOCITY_ACCUMULATE_358AC_SERVICE_29",
            "RECOVERED_VELOCITY_ACCUMULATE_358AC_SERVICE_30",
            "130.0", "200.0", "70.0",
            "recovered_velocity_accumulate_358ac_run"):
        if fragment not in text:
            raise AssertionError(
                f"velocity accumulation model missing {fragment}")

    # --- listing evidence 0x358ac-0x35c28 -----------------------------------
    listing = LISTING.read_text(encoding="utf-8")
    block = listing[listing.index("   358ac:"):listing.index("   35c2c:")]
    for evidence in (
            "mov\t6,r11", "st\tr11,0x884000",
            "ldos\t0x30(r8),g4", "cmpibe\t3,g4,0x36458",
            "ldos\t0x186(r8),g4", "ldos\t0x184(r8),g5",
            "shlo\t1,g4,g4", "addo\tg5,g4,g4", "stos\tg4,0x2e(r8)",
            "ldos\t0x19c(r8),g4", "cmpibe\t0,g4,0x3596c",
            "ld\t0x1c4(r8),g5", "ld\t0x7c(r8),g4", "cmpr\tg5,g4",
            "ble\t0x358f4", "ld\t0x7c(r8),r10", "st\tr10,0x1c4(r8)",
            "mov\t29,r11", "notbit\t31,g4,g4",
            "st\tg5,0x884000", "st\tg4,0x884000",
            "ld\t0x884000,g5", "ld\t0x1c8(r8),g4", "addr\tg5,g4,g5",
            "st\tg5,0x1c8(r8)", "mov\t30,r10", "lda\t0xffff,g4",
            "and\tg6,g4,g6", "ld\t0x884000,g4", "b\t0x35bcc",
            "ld\t0x1cc(r8),g5", "addr\tg4,g5,g4", "st\tg4,0x1cc(r8)",
            "cmpibne\t18,g4,0x35c3c", "ld\t0x51ab14,g6",
            "ld\t0x670(g6),g4", "mov\t30,r11"):
        if evidence not in block:
            raise AssertionError(
                f"velocity accumulation listing evidence missing: {evidence}")

    # The registered range stops at 0x35c28; the modelled span continues to the
    # 0x35cd4 boundary, so the state-11 arm is checked over the full listing.
    for evidence in (
            "cmpibne\t11,g4,0x35cd4", "ld\t0x678(g6),g4",
            "ld\t0x678(g6),g6", "st\tg4,0x1cc(r8)"):
        if evidence not in listing:
            raise AssertionError(
                f"velocity accumulation tail evidence missing: {evidence}")

    print("recovered velocity accumulation 358ac runnable: ok")


if __name__ == "__main__":
    main()
