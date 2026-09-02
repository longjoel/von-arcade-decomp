#!/usr/bin/env python3
"""Test the deterministic I/O self-test failure-reset slice."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_io.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-io-") as directory:
        library = Path(directory) / "io.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        reset = recovered.recovered_io_failure_reset
        reset.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.POINTER(ctypes.c_uint16),
        ]
        values = [ctypes.c_ubyte(0xA5) for _ in range(4)]
        halfword = ctypes.c_uint16(0x5AA5)
        reset(*(ctypes.pointer(value) for value in values), ctypes.pointer(halfword))
        if any(value.value != 0 for value in values) or halfword.value != 0:
            raise SystemExit("failure reset did not clear all five fields")

        fill = recovered.recovered_io_fill_input_indices
        fill.argtypes = [
            ctypes.POINTER(ctypes.c_uint16),
            ctypes.POINTER(ctypes.c_uint16),
        ]
        first = (ctypes.c_uint16 * 30)()
        second = (ctypes.c_uint16 * 30)()
        fill(first, second)
        if list(first) != list(range(30)) or list(second) != list(range(30, 60)):
            raise SystemExit("input index tables mismatch")

        plan = recovered.recovered_io_setup_plan
        plan.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_uint32]
        plan.restype = ctypes.c_uint32
        output = (ctypes.c_ubyte * 1170)()
        if plan(output, len(output)) != 1170:
            raise SystemExit("input setup plan length mismatch")
        first_setup = bytes((0x11, 0x11, 0x51, 0xD1, 0x71, 0xF1, 0x51,
                             0xD1, 0x51, 0xD1, 0x71, 0xF1, 0x51, 0xD1,
                             0x51, 0xD1, 0x51, 0xD1, 0x51, 0xD1, 0x51))
        second_setup = bytes((0x01, 0x01, 0x41, 0xC1, 0x61, 0xE1, 0x61, 0xE1, 0x41))
        if bytes(output) != first_setup * 30 + second_setup * 60:
            raise SystemExit("input setup byte plan mismatch")

        average = recovered.recovered_io_average_controller_bytes
        average.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_uint16]
        for sampled in range(256):
            state = (ctypes.c_ubyte * 8)(*range(8))
            average(state, sampled | 0xA500)
            if list(state) != [(index + sampled) >> 1 for index in range(8)]:
                raise SystemExit("controller-byte average mismatch")

        class Packed(ctypes.Structure):
            _fields_ = [
                ("status_49c", ctypes.c_uint32),
                ("status_498", ctypes.c_uint8),
                ("status_499", ctypes.c_uint8),
                ("status_49a", ctypes.c_uint8),
                ("work_a0", ctypes.c_uint32),
                ("work_a4", ctypes.c_uint32),
                ("work_a8", ctypes.c_uint32),
                ("work_ac", ctypes.c_uint32),
                ("work_b0", ctypes.c_uint32),
                ("work_b4", ctypes.c_uint32),
                ("work_b8", ctypes.c_uint32),
                ("work_bc", ctypes.c_uint32),
            ]

        pack = recovered.recovered_io_pack_controller_state
        pack.argtypes = [ctypes.c_uint32] * 7 + [ctypes.c_uint16] * 4 + [ctypes.POINTER(Packed)]
        for seed in (0, 1, 0x55555555, 0xAAAAAAAA, 0xFFFFFFFF):
            for port_2, port_4, port_6, port_c in (
                (0, 0, 0, 0), (0xFFFF, 0x1234, 0xABCD, 0x5678),
                (0x0040, 0x00FF, 0x8001, 0x00A5)):
                result = Packed()
                prior_ac = seed ^ 0x13579BDF
                prior_bc = seed ^ 0x2468ACE0
                pack(seed, 0x11111111, 0x22222222, prior_ac,
                     0x33333333, 0x44444444, prior_bc,
                     port_2, port_4, port_6, port_c, ctypes.byref(result))
                packed = ((port_6 & 0xFF) << 16) | ((port_4 & 0xFF) << 8) | (port_2 & 0xFF)
                first_mask = seed & packed
                second_mask = (~((port_2 >> 6) & 3)) & 0xFFFFFFFF
                expected = (tuple([(~packed) & 0xFFFFFFFF, port_c & 0xFF,
                                   port_c & 0xFF, port_c & 0xFF, seed,
                                   first_mask, first_mask, second_mask,
                                   prior_ac, prior_ac & (~second_mask & 0xFFFFFFFF),
                                   second_mask & (~prior_ac & 0xFFFFFFFF), prior_bc]))
                actual = tuple(getattr(result, name) for name, _ in Packed._fields_)
                if actual != expected:
                    raise SystemExit(f"packed controller state mismatch: {actual} != {expected}")

        command = recovered.recovered_io_command_plan
        command.argtypes = [ctypes.c_uint16, ctypes.c_uint16,
                            ctypes.POINTER(ctypes.c_ubyte)]
        command.restype = ctypes.c_uint32
        prefix = bytes((0x11, 0x11, 0x51, 0xD1, 0x71, 0xF1, 0x51, 0xD1, 0x71))
        for input_index in range(60):
            for table_value in (0, 1, 0x8000, 0xFFFF, 0xA55A):
                command_output = (ctypes.c_ubyte * 34)()
                if command(input_index, table_value, command_output) != 34:
                    raise SystemExit("input command plan length mismatch")
                expected = bytearray(prefix)
                for bit in range(5):
                    pair = (0x71, 0xF1) if input_index & (1 << (5 + bit)) else (0x51, 0xD1)
                    expected.extend(pair)
                for bit in range(5):
                    pair = (0x71, 0xF1) if table_value & (1 << (15 - bit)) else (0x51, 0xD1)
                    expected.extend(pair)
                expected.extend((0x01, 0x01, 0x51, 0xD1, 0x51))
        if bytes(command_output) != bytes(expected):
                    raise SystemExit("input command byte plan mismatch")

        normal_plan = recovered.recovered_io_normal_input_plan
        normal_plan.argtypes = [ctypes.POINTER(ctypes.c_uint16),
                                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_uint32]
        normal_plan.restype = ctypes.c_uint32
        table = (ctypes.c_uint16 * 30)(*(index * 0x1234 & 0xFFFF for index in range(30)))
        schedule = (ctypes.c_ubyte * 3321)()
        if normal_plan(table, schedule, len(schedule)) != 3321:
            raise SystemExit("normal input schedule length mismatch")
        cursor = 0
        for bank in range(2):
            for index in range(30):
                if bytes(schedule[cursor:cursor + 21]) != first_setup:
                    raise SystemExit("normal input setup ordering mismatch")
                cursor += 21
                command_expected = (ctypes.c_ubyte * 34)()
                command(index + bank * 30, table[index], command_expected)
                if bytes(schedule[cursor:cursor + 34]) != bytes(command_expected):
                    raise SystemExit("normal input command ordering mismatch")
                cursor += 34
        if cursor != 3300:
            raise SystemExit("normal input schedule cursor mismatch")
        final_setup = bytes((0x11, 0x11, 0x51, 0xD1, 0x71, 0xF1, 0x51,
                             0xD1, 0x51, 0xD1, 0x51, 0xD1, 0x51, 0xD1,
                             0x51, 0xD1, 0x51, 0xD1, 0x51, 0xD1, 0x51))
        if bytes(schedule[cursor:cursor + 21]) != final_setup:
            raise SystemExit("normal input final setup mismatch")
        cursor += 21
        if cursor != 3321:
            raise SystemExit("normal input schedule cursor mismatch")

        class Sample(ctypes.Structure):
            _fields_ = [
                ("status_3f0", ctypes.c_uint8),
                ("status_480", ctypes.c_uint8),
                ("status_481", ctypes.c_uint8),
                ("status_482", ctypes.c_uint8),
                ("latched_value", ctypes.c_uint16),
            ]

        sample = recovered.recovered_io_sample_input
        sample.argtypes = [ctypes.c_uint8, ctypes.c_uint16, ctypes.c_uint16,
                           ctypes.POINTER(Sample)]
        for input_byte in (0, 1, 0x55, 0xAA, 0xFF):
            for port_word in (0, 1, 0x5A, 0xA5, 0xFFFF):
                result = Sample()
                sample(input_byte, port_word, 0x1234, ctypes.byref(result))
                expected_port = port_word & 0xFF
                expected = (input_byte & expected_port, expected_port,
                            input_byte, (~expected_port) & 0xFF, 0x1234)
                actual = (result.status_3f0, result.status_480,
                          result.status_481, result.status_482,
                          result.latched_value)
                if actual != expected:
                    raise SystemExit(f"input sample mismatch: {actual} != {expected}")

    print("recovered I/O reset, input-index, command-plan, setup-plan, sampler, average, and packed-state vectors: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
