#!/usr/bin/env python3
"""Exhaustively test the bounded audio helper slices."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_audio_queue.c"
CONTROL_SOURCE = ROOT / "von/i960/recovered_host_control.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-audio-helpers-") as directory:
        library = Path(directory) / "audio-helpers.so"
        subprocess.run(
            [
                os.environ.get("CC", "cc"),
                "-shared",
                "-fPIC",
                "-O2",
                SOURCE,
                CONTROL_SOURCE,
                "-o",
                library,
            ],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))

        recovered.recovered_audio_clamp_level.argtypes = [ctypes.c_int32]
        recovered.recovered_audio_clamp_level.restype = ctypes.c_uint32
        recovered.recovered_audio_frame_bytes.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_ubyte),
        ]
        recovered.recovered_audio_frame_bytes.restype = ctypes.c_uint32
        recovered.recovered_audio_queue_init_fill_value.restype = ctypes.c_uint32
        recovered.recovered_audio_init_status_value.argtypes = [ctypes.c_uint32]
        recovered.recovered_audio_init_status_value.restype = ctypes.c_uint32

        clamp_vectors = 0
        values = list(range(-1024, 1025)) + [-(1 << 31), (1 << 31) - 1]
        for value in values:
            expected = 1 if value <= 0 else 127 if value > 127 else value
            actual = recovered.recovered_audio_clamp_level(value)
            if actual != expected:
                raise SystemExit(f"clamp mismatch value={value}: {actual} != {expected}")
            clamp_vectors += 1

        frame_vectors = 0
        for value in range(0x10000):
            for selector in (0, 1, 4, 0xFF):
                output = (ctypes.c_ubyte * 3)()
                count = recovered.recovered_audio_frame_bytes(value, selector, output)
                actual = bytes(output[:count])
                expected = bytes((0xA0, selector, value & 0xFF))
                if actual != expected or count != 3:
                    raise SystemExit(
                        f"frame mismatch value=0x{value:04x}, selector={selector}"
                    )
                frame_vectors += 1

        if recovered.recovered_audio_queue_init_fill_value() != 0x99:
            raise SystemExit("audio queue initialization fill mismatch")
        expected_status = (0, 0, 0, 0x40, 0x4E, 0x37)
        for index, expected in enumerate(expected_status):
            actual = recovered.recovered_audio_init_status_value(index)
            if actual != expected:
                raise SystemExit(
                    f"SCSP initialization status mismatch index={index}: "
                    f"0x{actual:x} != 0x{expected:x}"
                )

    print(
        f"PASS: {clamp_vectors:,} clamp, {frame_vectors:,} frame, "
        f"and {len(expected_status)} SCSP initialization vectors"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
