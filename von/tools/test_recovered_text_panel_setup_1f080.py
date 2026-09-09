#!/usr/bin/env python3
"""Test the current-origin text panel route at 0x1f080."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text_panel_setup_1f080.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("timing_cdc", "timing_ce0", "timing_ce4", "helper",
                 "source", "width", "rows")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-text-panel-1f080-") as directory:
        library = Path(directory) / "text-panel.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_text_panel_setup_1f080_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(1, 12, ctypes.byref(plan))
        assert (plan.timing_cdc, plan.timing_ce0, plan.timing_ce4,
                plan.helper, plan.source, plan.width, plan.rows) == (
            19, 19, 43, 0x1DC90, 0x02FE077E, 23, 5)
        plan_fn(0, 0xFFFFFFFF, ctypes.byref(plan))
        assert (plan.timing_ce4, plan.helper, plan.source,
                plan.width, plan.rows) == (30, 0x1DF00, 0, 23, 5)

    print("PASS: 0x1f080 current-origin text panel route")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
