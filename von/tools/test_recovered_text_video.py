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
        recovered.recovered_word_expand.argtypes = [ctypes.c_uint32]
        recovered.recovered_word_expand.restype = ctypes.c_uint32
        recovered.recovered_word_expand_blocks.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_uint32,
        ]
        recovered.recovered_word_expand_blocks.restype = None
        recovered.recovered_halfword_byte_swap.argtypes = [ctypes.c_uint32]
        recovered.recovered_halfword_byte_swap.restype = ctypes.c_uint32
        recovered.recovered_halfword_byte_swap_copy.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_uint32,
        ]
        recovered.recovered_halfword_byte_swap_copy.restype = None
        recovered.recovered_text_startup_asset_transfer_plan.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
        ]
        recovered.recovered_text_startup_asset_transfer_plan.restype = ctypes.c_uint32
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

        word_vectors = 0
        for value in range(0x10000):
            expected = (
                ((value & 0x000F) << 1)
                | ((value & 0x1000) >> 12)
                | ((value & 0x00F0) << 2)
                | ((value & 0x2000) >> 8)
                | ((value & 0x0F00) << 3)
                | ((value & 0x4000) >> 4)
            )
            actual = recovered.recovered_word_expand(value)
            if actual != expected:
                raise SystemExit(
                    f"word expand mismatch value=0x{value:04x}: "
                    f"0x{actual:04x} != 0x{expected:04x}"
                )
            word_vectors += 1

        block_vectors = 0
        for blocks in (0, 1, 2, 8):
            source = (ctypes.c_uint16 * max(1, blocks * 16))()
            destination = (ctypes.c_uint16 * max(1, blocks * 16))()
            for index in range(blocks * 16):
                source[index] = (index * 0x1357 + 0x2468) & 0xFFFF
                destination[index] = 0xA5A5
            recovered.recovered_word_expand_blocks(destination, source, blocks)
            for index in range(blocks * 16):
                value = source[index]
                expected = (
                    ((value & 0x000F) << 1)
                    | ((value & 0x1000) >> 12)
                    | ((value & 0x00F0) << 2)
                    | ((value & 0x2000) >> 8)
                    | ((value & 0x0F00) << 3)
                    | ((value & 0x4000) >> 4)
                )
                if destination[index] != expected:
                    raise SystemExit(
                        f"block expand mismatch blocks={blocks} index={index}"
                    )
                block_vectors += 1

        swap_vectors = 0
        for value in range(0x10000):
            expected = ((value & 0x00FF) << 8) | ((value & 0xFF00) >> 8)
            actual = recovered.recovered_halfword_byte_swap(value)
            if actual != expected:
                raise SystemExit(
                    f"halfword swap mismatch value=0x{value:04x}: "
                    f"0x{actual:04x} != 0x{expected:04x}"
                )
            swap_vectors += 1

        swap_block_vectors = 0
        for halfwords in (0, 1, 2, 31, 128):
            source = (ctypes.c_uint16 * max(1, halfwords))()
            destination = (ctypes.c_uint16 * max(1, halfwords))()
            for index in range(halfwords):
                source[index] = (index * 0x5317 + 0x2468) & 0xFFFF
                destination[index] = 0xA5A5
            recovered.recovered_halfword_byte_swap_copy(
                destination, source, halfwords
            )
            for index in range(halfwords):
                value = source[index]
                expected = ((value & 0x00FF) << 8) | ((value & 0xFF00) >> 8)
                if destination[index] != expected:
                    raise SystemExit(
                        f"halfword swap copy mismatch count={halfwords} index={index}"
                    )
                swap_block_vectors += 1

        startup_expected = {
            0: (
                (0, 0x01800020, 0x02FDEF20, 0x31),
                (0, 0x01801020, 0x02FDF540, 0x31),
                (0, 0x01800640, 0x02FD6EA0, 0x2E),
                (0, 0x01801640, 0x02FD7460, 0x2E),
                (0, 0x01800C00, 0x02FF7568, 0x0D),
                (0, 0x01801C00, 0x02FF7568, 0x0D),
                (1, 0x01081000, 0x02E21A74, 0x18800),
                (1, 0x010B2000, 0x02E21054, 0x17000),
                (1, 0x010E0000, 0x02E6DB14, 0x6800),
            ),
            1: (
                (0, 0x01800020, 0x02FDEF20, 0x31),
                (0, 0x01801020, 0x02FDF540, 0x31),
                (0, 0x01800640, 0x02FED0E8, 0x4E),
                (0, 0x01801640, 0x02FEDAA8, 0x4E),
                (1, 0x01081000, 0x02E21A74, 0x18800),
                (1, 0x010B2000, 0x02E4E0D4, 0x27000),
            ),
        }
        startup_tail = (
            (1, 0x010A9100, 0x00144CC4, 0x770),
            (1, 0x00FFB600, 0x00146324, 0x480),
            (1, 0x00FFA200, 0x00144184, 0x5A0),
            (1, 0x00FFE800, 0x00145BA4, 0x3C0),
            (1, 0x00286F80, 0x00146C24, 0x20),
            (1, 0x01086FC0, 0x00146C64, 0x20),
            (2, 0x010AAE00, 0x9999, 0x10),
            (0, 0x01801520, 0x0001BB50, 1),
            (0, 0x01801F40, 0x0001BB70, 1),
            (0, 0x01801F60, 0x0001BB70, 1),
            (0, 0x01801FC0, 0x0001BB70, 1),
        )
        startup_vectors = 0
        for profile, expected_prefix in startup_expected.items():
            expected = expected_prefix + startup_tail
            for index, expected_transfer in enumerate(expected):
                kind = ctypes.c_uint32()
                destination = ctypes.c_uint32()
                source_or_value = ctypes.c_uint32()
                units = ctypes.c_uint32()
                valid = recovered.recovered_text_startup_asset_transfer_plan(
                    profile, index, ctypes.byref(kind), ctypes.byref(destination),
                    ctypes.byref(source_or_value), ctypes.byref(units)
                )
                actual = (kind.value, destination.value, source_or_value.value, units.value)
                if valid != 1 or actual != expected_transfer:
                    raise SystemExit(
                        f"startup transfer mismatch profile={profile} index={index}: {actual!r}"
                    )
                startup_vectors += 1
            if recovered.recovered_text_startup_asset_transfer_plan(
                profile, len(expected), ctypes.byref(kind), ctypes.byref(destination),
                ctypes.byref(source_or_value), ctypes.byref(units)
            ) != 0:
                raise SystemExit(f"startup plan did not terminate profile={profile}")

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
        f"{copy_vectors} row copies, {word_vectors:,} word expansions, "
        f"{block_vectors} block expansions, {swap_vectors:,} halfword swaps, "
        f"{swap_block_vectors} swap copies, {startup_vectors} startup transfers, "
        f"and {plan_vectors:,} row-transfer plan entries"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
