#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_calibration_flag_gate_921d8.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("921d8", "cmpi"), ("921dc", "st"),
                      ("921ec", "st"), ("921f4", "be"),
                      ("921f8", "cmpibe")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "flag_value", "emitted_word_0", "emitted_word_1", "emitted_word_2",
        "completion_target", "helper_gate_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "gate.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_calibration_flag_gate_921d8
    function.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]
    plan = Plan()
    function(0, ctypes.byref(plan))
    assert (plan.flag_value, plan.emitted_word_0, plan.emitted_word_1,
            plan.emitted_word_2, plan.completion_target, plan.helper_gate_target) == (
                0, 0x3e4ccccd, 0x3e4ccccd, 0x3e4ccccd, 0x9224c, 0x921f8)
    function(1, ctypes.byref(plan))
    assert plan.flag_value == 1

print("recovered geometry 0x921d8 calibration-flag gate fixture: ok")
