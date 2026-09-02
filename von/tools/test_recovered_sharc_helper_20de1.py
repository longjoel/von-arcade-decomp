#!/usr/bin/env python3
"""Validate the recovered SHARC 0x20de1 plane-interpolation model."""

import ctypes
import math
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_helper_20de1.c"
RECIPROCAL_SOURCE = ROOT / "von/i960/recovered_sharc_opcode_35.c"


def f32(value):
    return ctypes.c_float(value).value


def words(points):
    return (ctypes.c_uint32 * 12)(*(
        ctypes.c_uint32.from_buffer_copy(ctypes.c_float(value)).value
        for point in points for value in point
    ))


def main() -> int:
    records = [
        ((1, 2, 5), (4, 7, 6), (9, 8, 3), (10, 11, 12)),
        ((2, 2, 5), (4, 7, 6), (9, 8, 3), (10, 11, 12)),
        ((1, 3, 5), (4, 8, 6), (9, 9, 3), (10, 12, 12)),
        ((2, 2, 5), (5, 7, 6), (10, 8, 3), (11, 11, 12)),
    ]
    expected = [
        lambda x, z: (30 * x + 9 * z - 1) / 37,
        lambda x, z: (12 * x + 3 * z - 13) / 13,
        lambda x, z: (30 * x + 9 * z + 36) / 37,
        lambda x, z: (30 * x + 9 * z - 31) / 37,
    ]
    samples = ((0, 0), (1, 0), (0, 1), (0.5, 0.5), (-1.25, 2.0))

    with tempfile.TemporaryDirectory(prefix="von-sharc-20de1-") as directory:
        library_path = pathlib.Path(directory) / "helper.so"
        subprocess.run(
            ["cc", "-std=c99", "-shared", "-fPIC", "-O2", str(SOURCE),
             str(RECIPROCAL_SOURCE),
             "-o", str(library_path)], check=True
        )
        library = ctypes.CDLL(str(library_path))
        plane_y = library.recovered_sharc_helper_20de1_plane_y
        plane_y.argtypes = [
            ctypes.POINTER(ctypes.c_uint32), ctypes.c_float, ctypes.c_float,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        plane_y.restype = ctypes.c_int

        equality_tail = library.recovered_sharc_helper_20de1_equality_tail
        equality_tail.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        equality_tail.restype = ctypes.c_int
        if equality_tail(0x3f800000, 0x3f800000) != 1:
            raise SystemExit("equal finite helper products were rejected")
        if equality_tail(0x00000000, 0x80000000) != 1:
            raise SystemExit("signed-zero helper products were rejected")
        if equality_tail(0x3f800000, 0x3f800001) != 0:
            raise SystemExit("distinct helper products were accepted")

        equality_schedule = library.recovered_sharc_helper_20de1_equality_schedule
        equality_schedule.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
            ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
        ]
        equality_schedule.restype = ctypes.c_int

        def schedule(*values):
            f9 = ctypes.c_uint32()
            f14 = ctypes.c_uint32()
            f2 = ctypes.c_uint32()
            result = equality_schedule(*values, ctypes.byref(f9),
                                        ctypes.byref(f14), ctypes.byref(f2))
            return result, f9.value, f14.value, f2.value

        # The rebuilt four-case sentinel capture has three records with
        # F11=0 and one with F11=1; all share F13=old F14=old F15=0.
        for f11 in (0x00000000, 0x3f800000):
            result, f9, f14, f2 = schedule(
                f11, 0x00000000, 0x00000000, 0x00000000)
            if result != 1 or f9 != f14 or f2 != 0x00000000:
                raise SystemExit(
                    f"sentinel equality schedule mismatch: {f11:08x} "
                    f"f9={f9:08x} f14={f14:08x} f2={f2:08x}"
                )

        # The normal captured tuple is F11=8, F13=1, old F14=2, old F15=2.
        result, f9, f14, f2 = schedule(
            0x41000000, 0x3f800000, 0x40000000, 0x40000000)
        if result != 0 or (f9, f14, f2) != (0x449f0000, 0x42280000, 0x4499c000):
            raise SystemExit(
                f"normal equality schedule mismatch: "
                f"f9={f9:08x} f14={f14:08x} f2={f2:08x}"
            )

        for record, formula in zip(records, expected):
            record_words = words(record)
            for x, z in samples:
                result = ctypes.c_uint32(0xdeadbeef)
                status = plane_y(record_words, f32(x), f32(z), ctypes.byref(result))
                actual = ctypes.c_float.from_buffer_copy(
                    result.value.to_bytes(4, "little")
                ).value
                target = formula(f32(x), f32(z))
                if status != 1 or not math.isclose(actual, target, rel_tol=0, abs_tol=2e-6):
                    raise SystemExit(
                        f"plane mismatch record={record!r} x={x} z={z}: "
                        f"status={status} actual={actual} expected={target}"
                    )

        degenerate = words(((0, 0, 0), (1, 0, 0), (1, 0, 0), (0, 1, 0)))
        result = ctypes.c_uint32(0xdeadbeef)
        if plane_y(degenerate, 0.0, 0.0, ctypes.byref(result)) != 0:
            raise SystemExit("zero-y-normal record was not rejected")
        if result.value != 0xdeadbeef:
            raise SystemExit("degenerate helper modified its result")

    print("recovered SHARC helper 0x20de1 plane model: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
