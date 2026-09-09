#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_calibration_secondary_threshold_gate_916d8.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("916d8", "lda"), ("916dc", "cmpibg"),
                      ("916e0", "ldq"), ("9174c", "lda")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "source_value", "threshold_value", "low_path_target", "high_path_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "gate.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_calibration_secondary_threshold_gate_916d8
    function.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]
    plan = Plan()
    function(0x8b, ctypes.byref(plan))
    assert (plan.source_value, plan.threshold_value, plan.low_path_target,
            plan.high_path_target) == (0x8b, 0x8b, 0x91a74, 0x9174c)
    function(0x8c, ctypes.byref(plan))
    assert plan.source_value == 0x8c

print("recovered geometry 0x916d8 threshold-gate fixture: ok")
