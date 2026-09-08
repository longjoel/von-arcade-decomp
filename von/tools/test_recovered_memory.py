#!/usr/bin/env python3
"""Check the recovered i960 forward-copy primitive."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_memory.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-memory-") as directory:
        library = Path(directory) / "memory.so"
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
        recovered.recovered_memory_copy_forward.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_uint32,
        ]
        recovered.recovered_memory_copy_forward.restype = None
        recovered.recovered_memory_copy_overlap.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_uint32,
        ]
        recovered.recovered_memory_copy_overlap.restype = None
        recovered.recovered_state_shift_77de0.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p
        ]
        recovered.recovered_state_shift_77de0.restype = None
        recovered.recovered_state_shift_77e20.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p
        ]
        recovered.recovered_state_shift_77e20.restype = None

        vectors = 0
        for source_alignment in range(16):
            for destination_alignment in range(16):
                for length in range(129):
                    source = (ctypes.c_ubyte * 160)()
                    destination = (ctypes.c_ubyte * 160)()
                    for index in range(160):
                        source[index] = (index * 37 + 11) & 0xFF
                        destination[index] = 0xA5
                    recovered.recovered_memory_copy_forward(
                        ctypes.byref(destination, destination_alignment),
                        ctypes.byref(source, source_alignment),
                        length,
                    )
                    actual = bytes(destination)
                    expected = bytearray(b"\xA5" * 160)
                    expected[destination_alignment:destination_alignment + length] = (
                        bytes(source[source_alignment:source_alignment + length])
                    )
                    if actual != bytes(expected):
                        raise SystemExit(
                            "copy mismatch "
                            f"source_alignment={source_alignment} "
                            f"destination_alignment={destination_alignment} length={length}"
                        )
                    vectors += 1

        overlap_vectors = 0
        for source_offset in range(8):
            for destination_offset in range(8):
                for length in range(65):
                    storage = (ctypes.c_ubyte * 96)()
                    initial = bytearray(
                        (index * 29 + 7) & 0xFF for index in range(96)
                    )
                    for index, value in enumerate(initial):
                        storage[index] = value
                    expected = bytearray(initial)
                    expected[destination_offset:destination_offset + length] = (
                        initial[source_offset:source_offset + length]
                    )
                    recovered.recovered_memory_copy_overlap(
                        ctypes.byref(storage, destination_offset),
                        ctypes.byref(storage, source_offset),
                        length,
                    )
                    assert bytes(storage) == bytes(expected)
                    overlap_vectors += 1

        current = (ctypes.c_ubyte * 0xf4)(*range(0xf4))
        previous = (ctypes.c_ubyte * 0xf4)(
            *((index + 1) & 0xff for index in range(0xf4))
        )
        next_state = (ctypes.c_ubyte * 0xf4)(*[0xA5] * 0xf4)
        recovered.recovered_state_shift_77de0(current, previous, next_state)
        assert bytes(current) == bytes(previous)
        assert bytes(next_state) == bytes(previous)

        current = (ctypes.c_ubyte * 0xf4)(*[0xA5] * 0xf4)
        next_state = (ctypes.c_ubyte * 0xf4)(*range(0xf4))
        previous = (ctypes.c_ubyte * 0xf4)(
            *((index + 1) & 0xff for index in range(0xf4))
        )
        output = (ctypes.c_ubyte * 0xf4)(*[0x5A] * 0xf4)
        recovered.recovered_state_shift_77e20(
            current, next_state, output, previous
        )
        assert bytes(current) == bytes(next_state)
        assert bytes(output) == bytes(previous)

    print(
        f"PASS: {vectors:,} forward-copy and {overlap_vectors:,} "
        "overlap-copy vectors"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
