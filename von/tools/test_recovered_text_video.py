#!/usr/bin/env python3
"""Test the recovered text/video initialization plan."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-text-video-") as directory:
        library = Path(directory) / "text-video.so"
        subprocess.run(
            [
                os.environ.get("CC", "cc"),
                "-shared",
                "-fPIC",
                "-O2",
                SOURCE,
                "-o",
                library,
            ],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        recovered.recovered_text_video_clear_plan.argtypes = [
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
        ]
        recovered.recovered_text_video_clear_plan.restype = ctypes.c_uint32
        recovered.recovered_text_video_state_plan.argtypes = [
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
        ]
        recovered.recovered_text_video_state_plan.restype = ctypes.c_uint32

        clear_expected = (
            (0x01000000, 0x4000),
            (0x0100C000, 0x1000),
            (0x01008000, 0x0800),
            (0x0100A000, 8),
        )
        for index, (expected_address, expected_count) in enumerate(clear_expected):
            address = ctypes.c_uint32()
            count = ctypes.c_uint32()
            valid = recovered.recovered_text_video_clear_plan(
                index, ctypes.byref(address), ctypes.byref(count)
            )
            if valid != 1 or (address.value, count.value) != (
                expected_address,
                expected_count,
            ):
                raise SystemExit(
                    f"video clear plan mismatch index={index}: "
                    f"0x{address.value:08x}/{count.value}"
                )

        state_expected = (
            (0x00504D24, 0),
            (0x00504D26, 0),
            (0x00504D28, 0),
            (0x00504D2A, 0),
            (0x00504D2C, 0),
            (0x00504D2E, 0),
            (0x00504D32, 0x4000),
            (0x00504D34, 0),
            (0x00504D38, 0),
        )
        for index, (expected_address, expected_value) in enumerate(state_expected):
            address = ctypes.c_uint32()
            value = ctypes.c_uint32()
            valid = recovered.recovered_text_video_state_plan(
                index, ctypes.byref(address), ctypes.byref(value)
            )
            if valid != 1 or (address.value, value.value) != (
                expected_address,
                expected_value,
            ):
                raise SystemExit(
                    f"video state plan mismatch index={index}: "
                    f"0x{address.value:08x}/0x{value.value:08x}"
                )

        for function_name, limit in (
            ("recovered_text_video_clear_plan", 4),
            ("recovered_text_video_state_plan", 9),
        ):
            address = ctypes.c_uint32(0xDEADBEEF)
            value = ctypes.c_uint32(0xDEADBEEF)
            valid = getattr(recovered, function_name)(
                limit, ctypes.byref(address), ctypes.byref(value)
            )
            if valid != 0:
                raise SystemExit(f"invalid {function_name} index accepted")

    print("PASS: 4 video clear and 9 video state plan entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
