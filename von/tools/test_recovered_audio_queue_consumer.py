#!/usr/bin/env python3
"""Exhaustively test the recovered SCSP FIFO consumer boundary."""

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
    with tempfile.TemporaryDirectory(prefix="von-audio-consumer-") as directory:
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
        recovered.recovered_audio_queue_consume.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
        ]
        recovered.recovered_audio_queue_consume.restype = ctypes.c_uint32

        vectors = 0
        for read_index in range(64):
            queue = (ctypes.c_ubyte * 64)(*range(64))
            for write_index in range(64):
                for sound_status in (0, 1, 2, 3, 0xFF):
                    next_read = ctypes.c_uint32(0xDEADBEEF)
                    value = ctypes.c_uint32(0xDEADBEEF)
                    consumed = recovered.recovered_audio_queue_consume(
                        read_index,
                        write_index,
                        sound_status,
                        queue,
                        ctypes.byref(next_read),
                        ctypes.byref(value),
                    )
                    expected = read_index != write_index and (sound_status & 1) != 0
                    if bool(consumed) != expected:
                        raise SystemExit(
                            f"consume mismatch read={read_index}, write={write_index}, "
                            f"status={sound_status}"
                        )
                    if expected:
                        if next_read.value != (read_index + 1) & 0x3F:
                            raise SystemExit("read-index advance mismatch")
                        if value.value != read_index:
                            raise SystemExit("queue-byte mismatch")
                    elif next_read.value != 0xDEADBEEF or value.value != 0xDEADBEEF:
                        raise SystemExit("empty/not-ready path modified outputs")
                    vectors += 1

    print(f"PASS: {vectors:,} audio consumer vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
