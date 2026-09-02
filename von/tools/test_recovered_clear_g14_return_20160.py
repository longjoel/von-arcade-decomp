#!/usr/bin/env python3
"""Test the 0x20160 clear-g14 indirect-return thunk contract."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_clear_g14_return_20160.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("return_stub", "clears_g14", "branch_register")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-clear-g14-20160-") as directory:
        library = Path(directory) / "clear-g14-20160.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_clear_g14_return_20160_plan
        plan_fn.argtypes = [ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(ctypes.byref(plan))
        assert (plan.return_stub, plan.clears_g14, plan.branch_register) == (0x20174, 1, 0)

    print("PASS: 0x20160 clear-g14 return thunk")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
