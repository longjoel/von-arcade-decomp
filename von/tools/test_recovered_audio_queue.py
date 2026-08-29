#!/usr/bin/env python3
"""Exhaustively test the recovered host-to-SCSP FIFO framing."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_audio_queue.c"
CONTROL_SOURCE = ROOT / "von/i960/recovered_host_control.c"


def expected_bytes(value: int, mode: int, board_status: int) -> bytes:
    value &= 0xFFFF
    if value == 0x00FF:
        return bytes((0xFF,))
    if mode == 1 and (board_status & 0xFF) == 2:
        return b""
    return bytes((0xAE, value >> 8, value & 0xFF))


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-audio-queue-") as directory:
        library = Path(directory) / "audio-queue.so"
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
        recovered.recovered_audio_command_bytes.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_ubyte),
        ]
        recovered.recovered_audio_command_bytes.restype = ctypes.c_uint32
        recovered.recovered_audio_command_bytes_for_status.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_ubyte),
        ]
        recovered.recovered_audio_command_bytes_for_status.restype = ctypes.c_uint32
        recovered.recovered_audio_queue_has_space.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        recovered.recovered_audio_queue_has_space.restype = ctypes.c_uint32
        recovered.recovered_audio_short_delay_iterations.restype = ctypes.c_uint32

        if recovered.recovered_audio_short_delay_iterations() != 4:
            raise SystemExit("short delay iteration count mismatch")

        vectors = 0
        for value in range(0x10000):
            for mode, board_status in ((0, 0), (1, 2), (1, 0), (2, 2)):
                output = (ctypes.c_ubyte * 3)()
                count = recovered.recovered_audio_command_bytes(
                    value, mode, board_status, output
                )
                actual = bytes(output[:count])
                expected = expected_bytes(value, mode, board_status)
                if actual != expected:
                    raise SystemExit(
                        f"framing mismatch value=0x{value:04x}, mode={mode}, "
                        f"status={board_status}: {actual.hex()} != {expected.hex()}"
                    )
                vectors += 1

        status_vectors = 0
        for value in range(0x10000):
            for mode in range(3):
                for board_status, suppressed_status in (
                    (0, 0),
                    (0, 2),
                    (2, 0),
                    (2, 2),
                    (0x102, 2),
                ):
                    output = (ctypes.c_ubyte * 3)()
                    count = recovered.recovered_audio_command_bytes_for_status(
                        value, mode, board_status, suppressed_status, output
                    )
                    value16 = value & 0xFFFF
                    if value16 == 0xFF:
                        expected = bytes((0xFF,))
                    elif mode == 1 and (board_status & 0xFF) == (
                        suppressed_status & 0xFF
                    ):
                        expected = b""
                    else:
                        expected = bytes((0xAE, value16 >> 8, value16 & 0xFF))
                    actual = bytes(output[:count])
                    if actual != expected:
                        raise SystemExit(
                            "parameterized framing mismatch "
                            f"value=0x{value:04x}, mode={mode}, "
                            f"status={board_status}, suppressed={suppressed_status}"
                        )
                    status_vectors += 1

        capacity_vectors = 0
        for read_index in range(64):
            for write_index in range(64):
                available = (read_index - write_index - 1) & 0x3F
                for count in range(65):
                    actual = bool(
                        recovered.recovered_audio_queue_has_space(
                            read_index, write_index, count
                        )
                    )
                    if actual != (available >= count):
                        raise SystemExit(
                            f"capacity mismatch read={read_index}, write={write_index}, "
                            f"count={count}"
                        )
                    capacity_vectors += 1

    print(
        f"PASS: {vectors:,} framing, {status_vectors:,} parameterized framing, "
        f"and {capacity_vectors:,} capacity vectors"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
