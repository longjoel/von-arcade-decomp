#!/usr/bin/env python3
"""Test the profile-selected 0x201a0 video upload contract."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_video_profile_upload.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("source", "destination", "flags", "halfwords_per_row", "rows", "origin", "helper")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-video-profile-") as directory:
        library = Path(directory) / "video-profile.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_video_profile_upload_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()
        for profile, destination in ((0, 0x1FCFD20), (1, 0x1FD49D0), (2, 0x1FD1520), (99, 0x1FD1520)):
            plan_fn(profile, 7, 17, ctypes.byref(plan))
            assert (plan.source, plan.destination, plan.flags,
                    plan.halfwords_per_row, plan.rows, plan.origin,
                    plan.helper) == (0x1004000, destination, 0x40, 0x40, 48, 7, 0x1BC90)

    print("PASS: 0x201a0 profile-selected video upload")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
