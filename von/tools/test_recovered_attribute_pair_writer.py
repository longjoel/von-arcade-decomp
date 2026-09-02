#!/usr/bin/env python3
"""Test the direct attribute-pair writer at 0x20300."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_attribute_pair_writer.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("return_stub", "source_first", "source_second", "destination_first",
                 "destination_second", "byte_offset", "attribute_bits")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-attribute-pair-") as directory:
        library = Path(directory) / "attribute-pair.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_attribute_pair_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
        plan = Plan()
        plan_fn(0, 3, ctypes.byref(plan))
        assert (plan.return_stub, plan.source_first, plan.source_second,
                plan.destination_first, plan.destination_second,
                plan.byte_offset, plan.attribute_bits) == (0x2038C, 0x2FE3214,
                                                           0x2FE3216, 0x1001288,
                                                           0x100128A, 42, 0xC000)
        plan_fn(1, 0, ctypes.byref(plan))
        assert (plan.source_first, plan.source_second, plan.destination_first,
                plan.destination_second) == (0x2FE3218, 0x2FE321A, 0x1001290, 0x1001292)

    print("PASS: 0x20300 attribute-pair writer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
