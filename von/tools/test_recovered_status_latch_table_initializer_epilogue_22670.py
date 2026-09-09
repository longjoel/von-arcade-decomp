#!/usr/bin/env python3
"""Validate the 0x22670 ABI epilogue contract."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_status_latch_table_initializer_epilogue_22670.c"


class Plan(ctypes.Structure):
    _fields_ = [
        ("integer_quad_restore_count", ctypes.c_uint32),
        ("g13_restore_offset", ctypes.c_uint32),
        ("g14_restore_offset", ctypes.c_uint32),
        ("floating_restore_count", ctypes.c_uint32),
        ("floating_offsets", ctypes.c_uint32 * 4),
        ("return_instruction", ctypes.c_uint32),
    ]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-epilogue-") as directory:
        library = Path(directory) / "epilogue.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        epilogue_fn = recovered.recovered_status_latch_table_initializer_epilogue_plan
        epilogue_fn.argtypes = [ctypes.POINTER(Plan)]
        plan = Plan()
        epilogue_fn(ctypes.byref(plan))
        assert (plan.integer_quad_restore_count, plan.g13_restore_offset,
                plan.g14_restore_offset, plan.floating_restore_count,
                list(plan.floating_offsets), plan.return_instruction) == (
                    2, 0x40, 0x44, 4, [0x48, 0x58, 0x68, 0x78], 0xA)

    print("PASS: 0x22670 status-latch table initializer epilogue")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
