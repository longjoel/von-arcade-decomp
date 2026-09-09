#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_calibration_secondary_entry_91e60.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("91e60", "lda"), ("91e64", "stq"),
                      ("91e6c", "mov"), ("91e7c", "ld"),
                      ("91e88", "lda"),
                      ("91e90", "lda"), ("91e98", "cmpi"),
                      ("91e9c", "lda")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())


class Input(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "argument_g0", "argument_g1", "argument_g2", "source_value")]


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "saved_g2", "source_value", "threshold_value", "table_base", "table_address",
        "preserved_g0", "preserved_g1", "preserved_g2", "first_partition_target",
        "upper_partition_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "entry.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_calibration_secondary_entry_91e60
    function.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    sample = Input(1, 2, 3, 0x12b)
    plan = Plan()
    function(ctypes.byref(sample), ctypes.byref(plan))
    assert (plan.saved_g2, plan.source_value, plan.threshold_value, plan.table_base,
            plan.table_address, plan.preserved_g0, plan.preserved_g1, plan.preserved_g2,
            plan.first_partition_target, plan.upper_partition_target) == (
                3, 0x12b, 0x12b, 0x2b46134, 0x2b80f64, 1, 2, 3, 0x91e98, 0x91ecc)

print("recovered geometry 0x91e60 calibration-entry fixture: ok")
