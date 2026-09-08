#!/usr/bin/env python3
"""Check the literal scan geometry and output contract at i960 0x77c40."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_record_flag_scan_77c40.c"


class Plan(ctypes.Structure):
    _fields_ = [
        ("record_base_offset", ctypes.c_uint32),
        ("record_stride", ctypes.c_uint32),
        ("record_count", ctypes.c_uint32),
        ("output_address", ctypes.c_uint32),
        ("count_threshold", ctypes.c_uint32),
        ("first_pass_count_bit", ctypes.c_uint32),
        ("first_pass_output_bits", ctypes.c_uint32),
        ("second_pass_count_bit", ctypes.c_uint32),
        ("second_pass_output_bits", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory(prefix="von-record-flag-scan-") as directory:
    library = Path(directory) / "record-flag-scan.so"
    subprocess.run(
        [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
        check=True,
    )
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_record_flag_scan_77c40_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    function.restype = None
    plan = Plan()
    function(ctypes.byref(plan))
    assert (
        plan.record_base_offset, plan.record_stride, plan.record_count,
        plan.output_address, plan.count_threshold,
    ) == (0x200, 0x20, 32, 0x00504E50, 20)
    assert (
        plan.first_pass_count_bit, plan.first_pass_output_bits,
        plan.second_pass_count_bit, plan.second_pass_output_bits,
    ) == (13, 0xC8, 13, 0x34)

print("recovered record-flag scan structural plan: ok")
