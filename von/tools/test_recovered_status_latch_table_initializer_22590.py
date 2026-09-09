#!/usr/bin/env python3
"""Validate the bounded 0x22590 table initializer."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_status_latch_table_initializer_22590.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "input_bit0", "fallback_first", "fallback_second", "g14_value",
        "first_destination", "second_destination", "first_source",
        "second_source", "destination_stride", "source_stride", "entry_count",
        "counter_address", "counter_before", "counter_after")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-table-init-") as directory:
        library = Path(directory) / "initializer.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        init_fn = recovered.recovered_status_latch_table_initializer_plan
        init_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.POINTER(Plan)]
        plan = Plan()

        init_fn(1, 0x12345678, 9, ctypes.byref(plan))
        assert (plan.input_bit0, plan.fallback_first, plan.fallback_second,
                plan.first_destination, plan.second_destination,
                plan.first_source, plan.second_source, plan.destination_stride,
                plan.source_stride, plan.entry_count, plan.counter_address,
                plan.counter_after) == (
                    1, 0x1DF, 0x7FE0, 0x51A0C0, 0x51A190, 0x180099C,
                    0x180099E, 8, 0x20, 25, 0x504D10, 10)
        init_fn(0, 0, 0xFFFFFFFF, ctypes.byref(plan))
        assert (plan.input_bit0, plan.counter_after) == (0, 0)

    print("PASS: 0x22590 status-latch table initializer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
