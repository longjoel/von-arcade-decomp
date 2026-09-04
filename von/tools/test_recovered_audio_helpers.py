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
        for name in ("recovered_audio_device_table_clear_plan",
                     "recovered_audio_service_table_reset_plan"):
            function = getattr(recovered, name)
            function.argtypes = [ctypes.c_uint32,
                                 ctypes.POINTER(ctypes.c_uint32),
                                 ctypes.POINTER(ctypes.c_uint32)]
            function.restype = ctypes.c_uint32
        recovered.recovered_audio_device_copy_plan.argtypes = [
            ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32)]
        recovered.recovered_audio_device_copy_plan.restype = ctypes.c_uint32
        recovered.recovered_audio_device_record_plan.argtypes = [
            ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32)]
        recovered.recovered_audio_device_record_plan.restype = ctypes.c_uint32
        recovered.recovered_audio_device_record_index.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        recovered.recovered_audio_device_record_index.restype = ctypes.c_uint32
        recovered.recovered_audio_device_buffer_copy.argtypes = [
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
        recovered.recovered_audio_device_buffer_copy.restype = None

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

        copy_expected = (
            (0x000f48d0, 0x01800000, 4, 0),
            (0x000f48d2, 0x01802000, 0, 0x000f48d0),
        )
        for index, expected in enumerate(copy_expected):
            source = ctypes.c_uint32()
            destination = ctypes.c_uint32()
            bytes_count = ctypes.c_uint32()
            count_source = ctypes.c_uint32()
            valid = recovered.recovered_audio_device_copy_plan(
                index, ctypes.byref(source), ctypes.byref(destination),
                ctypes.byref(bytes_count), ctypes.byref(count_source))
            if valid != 1 or (source.value, destination.value, bytes_count.value,
                              count_source.value) != expected:
                raise SystemExit(f"audio copy plan mismatch index={index}")
        address = ctypes.c_uint32()
        value = ctypes.c_uint32()
        for index in range(52):
            if recovered.recovered_audio_device_table_clear_plan(
                    index, ctypes.byref(address), ctypes.byref(value)) != 1:
                raise SystemExit("audio device clear plan ended early")
            if (address.value, value.value) != (0x0051a0c0 + index * 8, 0):
                raise SystemExit(f"audio device clear mismatch index={index}")
        for index in range(24):
            if recovered.recovered_audio_service_table_reset_plan(
                    index, ctypes.byref(address), ctypes.byref(value)) != 1:
                raise SystemExit("audio service reset plan ended early")
            if (address.value, value.value) != (0x00504c30 + index * 2, 0xffff):
                raise SystemExit(f"audio service reset mismatch index={index}")

        for index in range(23):
            source_record = ctypes.c_uint32()
            destination = ctypes.c_uint32()
            if recovered.recovered_audio_device_record_plan(
                    index, ctypes.byref(source_record), ctypes.byref(destination)) != 1:
                raise SystemExit("audio device record plan ended early")
            expected = (0x02bf83c8 + index * 8, 0x01802010 + index * 2)
            if (source_record.value, destination.value) != expected:
                raise SystemExit(f"audio record plan mismatch index={index}")

        index_vectors = 0
        for selector in range(0x10000):
            for exponent, mask in ((0, 0xffff), (1, 0xff), (7, 0x7fff),
                                   (15, 0xffff), (31, 0xffff)):
                actual = recovered.recovered_audio_device_record_index(
                    selector, exponent, mask)
                expected = (selector << exponent) & mask
                if actual != expected:
                    raise SystemExit("audio record index mismatch")
                index_vectors += 1

        words_per_row = 128
        source_buffer = (ctypes.c_uint32 * (96 * words_per_row))()
        destination_buffer = (ctypes.c_uint32 * (96 * words_per_row))()
        for index in range(96 * words_per_row):
            source_buffer[index] = (index * 0x1021 + 0x55aa) & 0xffffffff
            destination_buffer[index] = 0xdeadbeef
        recovered.recovered_audio_device_buffer_copy(
            destination_buffer, source_buffer)
        for row in range(96):
            for word in range(words_per_row):
                actual = destination_buffer[row * words_per_row + word]
                expected = (source_buffer[row * words_per_row + word]
                            if word < 64 else 0xdeadbeef)
                if actual != expected:
                    raise SystemExit(f"audio buffer copy mismatch row={row} word={word}")

    print(
        f"PASS: {clamp_vectors:,} clamp, {frame_vectors:,} frame, "
        f"and {len(expected_status)} SCSP initialization vectors, "
        f"2 device-copy, 52 device-clear, 24 service-reset, and "
        f"{index_vectors:,} device-index vectors, and 6,144 buffer-copy vectors"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
