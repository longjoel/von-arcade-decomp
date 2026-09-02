#!/usr/bin/env python3
"""Test the indexed status-code data table at 0x1f680."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_status_code_table.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("base", "record_count", "record_size", "blank_record_index",
                 "text_position_column", "text_position_row")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-code-table-") as directory:
        library = Path(directory) / "status-code-table.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        address = recovered.recovered_status_code_record_address
        address.argtypes = [ctypes.c_uint32]
        address.restype = ctypes.c_uint32
        assert [address(index) for index in (0, 1, 7, 8)] == [0x1F680, 0x1F690, 0x1F6F0, 0x1F700]
        assert address(9) == 0
        plan_fn = recovered.recovered_status_code_table_plan
        plan_fn.argtypes = [ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(ctypes.byref(plan))
        assert (plan.base, plan.record_count, plan.record_size, plan.blank_record_index,
                plan.text_position_column, plan.text_position_row) == (0x1F680, 9, 16, 8, 8, 14)

    print("PASS: 0x1f680 status-code table shape and bounds")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
