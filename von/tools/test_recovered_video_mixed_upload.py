#!/usr/bin/env python3
"""Test the ordered 0x20210 mixed upload sequence."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_video_mixed_upload.c"


class Record(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in ("source", "helper", "column", "row", "width", "height")]


class Plan(ctypes.Structure):
    _fields_ = [("origin", ctypes.c_uint32), ("record", Record * 5)]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-mixed-upload-") as directory:
        library = Path(directory) / "mixed-upload.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_mixed_upload_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(7, 99, 2, 4, 6, ctypes.byref(plan))
        assert plan.origin == 7
        expected = [(0x2FEFEE8, 0x1DC10, 7, 7, 64, 30),
                    (0x2FF16E8, 0x1DE80, 7, 7, 64, 33),
                    (0x2FF1568, 0x1DE80, 7, 33, 64, 4),
                    (0x2FF1568, 0x1DE80, 7, 7, 64, 4),
                    (0x2FF1568, 0x1DE80, 7, 37, 64, 4)]
        for record, values in zip(plan.record, expected):
            assert (record.source, record.helper, record.column, record.row,
                    record.width, record.height) == values

    print("PASS: 0x20210 mixed upload sequence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
