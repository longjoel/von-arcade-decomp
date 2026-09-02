#!/usr/bin/env python3
"""Test the 0x203d0/0x20400/0x20430 wrapper family."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_profile_upload_panel_wrappers.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("upload_source", "upload_destination", "upload_flags",
                 "upload_halfwords_per_row", "upload_rows", "upload_helper",
                 "panel_source_present", "panel_helper", "panel_column",
                 "panel_row", "panel_width", "panel_height")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-profile-panel-") as directory:
        library = Path(directory) / "profile-panel.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_profile_upload_panel_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(1, 1, 17, 9, ctypes.byref(plan))
        assert (plan.upload_source, plan.upload_destination, plan.upload_flags,
                plan.upload_halfwords_per_row, plan.upload_rows, plan.upload_helper,
                plan.panel_source_present, plan.panel_helper, plan.panel_column,
                plan.panel_row, plan.panel_height) == (0x1004000, 0x1FD49D0, 0x40,
                                                       0x40, 48, 0x1BC90, 1,
                                                       0x1DC90, 11, 21, 8)
        assert plan.panel_width == 40
        plan_fn(2, 0, 17, 9, ctypes.byref(plan))
        assert (plan.upload_destination, plan.panel_helper, plan.panel_source_present) == (0x1FD1520, 0x1DF00, 0)

    print("PASS: 0x203d0/0x20400/0x20430 wrapper family")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
