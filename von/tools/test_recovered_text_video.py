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
MEMORY_SOURCE = ROOT / "von/i960/recovered_memory.c"
HOST_CONTROL_SOURCE = ROOT / "von/i960/recovered_host_control.c"


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
                MEMORY_SOURCE,
                HOST_CONTROL_SOURCE,
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
        recovered.recovered_text_video_row_transfer_plan.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
        ]
        recovered.recovered_text_video_row_transfer_plan.restype = ctypes.c_uint32
        recovered.recovered_text_video_upload_plan.argtypes = [
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
        ]
        recovered.recovered_text_video_upload_plan.restype = ctypes.c_uint32
        recovered.recovered_text_video_copy_rows.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        recovered.recovered_text_video_copy_rows.restype = None
        recovered.recovered_text_voltage_warning_plan.argtypes = [
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
        ]
        recovered.recovered_text_voltage_warning_plan.restype = ctypes.c_uint32

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

        source = ctypes.c_uint32()
        destination_pointer = ctypes.c_uint32()
        halfwords = ctypes.c_uint32()
        rows = ctypes.c_uint32()
        valid = recovered.recovered_text_video_upload_plan(
            ctypes.byref(source),
            ctypes.byref(destination_pointer),
            ctypes.byref(halfwords),
            ctypes.byref(rows),
        )
        if valid != 1 or (
            source.value,
            destination_pointer.value,
            halfwords.value,
            rows.value,
        ) != (0x01004000, 0x02FD61D0, 0x40, 0x40):
            raise SystemExit("video upload plan mismatch")

        copy_vectors = 0
        for halfwords in (1, 2, 0x40):
            for rows in (0, 1, 2, 64):
                row_bytes = halfwords * 2
                source = (ctypes.c_ubyte * max(1, rows * 0x80))()
                destination = (ctypes.c_ubyte * max(1, rows * row_bytes))()
                for index in range(len(source)):
                    source[index] = (index * 13 + 7) & 0xFF
                for index in range(len(destination)):
                    destination[index] = 0xA5
                recovered.recovered_text_video_copy_rows(
                    source, destination, halfwords, rows
                )
                expected = bytearray(b"\xA5" * len(destination))
                for row in range(rows):
                    expected[row * row_bytes:(row + 1) * row_bytes] = (
                        bytes(source[row * 0x80:row * 0x80 + row_bytes])
                    )
                if bytes(destination) != bytes(expected):
                    raise SystemExit(
                        f"video row copy mismatch halfwords={halfwords} rows={rows}"
                    )
                copy_vectors += 1

        warning_expected = (
            (4, 16, 0x000012E0),
            (4, 19, 0x000012F0),
            (4, 25, 0x00001310),
            (20, 28, 0x00001320),
        )
        for index, expected in enumerate(warning_expected):
            column = ctypes.c_uint32()
            row = ctypes.c_uint32()
            text = ctypes.c_uint32()
            valid = recovered.recovered_text_voltage_warning_plan(
                index, ctypes.byref(column), ctypes.byref(row), ctypes.byref(text)
            )
            actual = (column.value, row.value, text.value)
            if valid != 1 or actual != expected:
                raise SystemExit(
                    f"warning plan mismatch index={index}: {actual!r} != {expected!r}"
                )
        column = ctypes.c_uint32(0xDEADBEEF)
        row = ctypes.c_uint32(0xDEADBEEF)
        text = ctypes.c_uint32(0xDEADBEEF)
        if recovered.recovered_text_voltage_warning_plan(
            4, ctypes.byref(column), ctypes.byref(row), ctypes.byref(text)
        ) != 0:
            raise SystemExit("accepted invalid warning record")

        plan_vectors = 0
        for rows in (0, 1, 2, 64, 255):
            for row in range(rows + 1):
                source = 0x1004000
                destination = 0x2000000
                halfwords = 0x40
                call_source = ctypes.c_uint32()
                call_destination = ctypes.c_uint32()
                call_bytes = ctypes.c_uint32()
                valid = recovered.recovered_text_video_row_transfer_plan(
                    row,
                    source,
                    destination,
                    halfwords,
                    rows,
                    ctypes.byref(call_source),
                    ctypes.byref(call_destination),
                    ctypes.byref(call_bytes),
                )
                expected_valid = row < rows
                if bool(valid) != expected_valid:
                    raise SystemExit(f"invalid row plan acceptance row={row} rows={rows}")
                if expected_valid:
                    expected_bytes = halfwords * 2
                    expected = (
                        source + row * 0x80,
                        destination + row * expected_bytes,
                        expected_bytes,
                    )
                    actual = (call_source.value, call_destination.value, call_bytes.value)
                    if actual != expected:
                        raise SystemExit(
                            f"row plan mismatch row={row} rows={rows}: "
                            f"{actual!r} != {expected!r}"
                        )
                plan_vectors += 1

    print(
        "PASS: 4 video clear, 9 video state, 1 upload, 4 warning records, "
        f"{copy_vectors} row copies, and {plan_vectors:,} row-transfer plan entries"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
