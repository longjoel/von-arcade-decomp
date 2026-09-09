#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_calibration_secondary_entry_91690.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("91690", "lda"), ("91694", "stq"),
                      ("9169c", "mov"), ("916ac", "ld"),
                      ("916b4", "lda"), ("916c8", "cmpi"),
                      ("916cc", "lda"), ("916d4", "ble")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())


class Input(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "argument_g0", "argument_g1", "argument_g2", "incoming_g14",
        "source_value", "g28_value")]


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "saved_g2", "saved_g14", "source_value", "threshold_limit", "table_base",
        "table_address", "preserved_g0", "preserved_g1", "first_target",
        "threshold_partition_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "entry.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_calibration_secondary_entry_91690
    function.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    sample = Input(1, 2, 3, 4, 0x120, 0x100)
    plan = Plan()
    function(ctypes.byref(sample), ctypes.byref(plan))
    assert (plan.saved_g2, plan.saved_g14, plan.source_value, plan.threshold_limit,
            plan.table_base, plan.table_address, plan.preserved_g0, plan.preserved_g1,
            plan.first_target, plan.threshold_partition_target) == (
                3, 4, 0x120, 0x11f, 0x2b46134, 0x2b80f64, 1, 2, 0x91a74, 0x916d8)

print("recovered geometry 0x91690 calibration-entry fixture: ok")
