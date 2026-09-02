#!/usr/bin/env python3
"""Test the fixed 0x1f060 video upload descriptor."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text_video_upload_wrapper.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("source", "destination", "halfwords_per_row", "rows")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-video-upload-wrapper-") as directory:
        library = Path(directory) / "video-upload-wrapper.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_text_video_upload_wrapper_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(4, ctypes.byref(plan))
        assert (plan.source, plan.destination, plan.halfwords_per_row, plan.rows) == (0x01004000, 0x02FD2520, 0x40, 35)
        plan_fn(0xFFFFFFFF, ctypes.byref(plan))
        assert plan.rows == 30

    print("PASS: 0x1f060 fixed video upload descriptor")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
