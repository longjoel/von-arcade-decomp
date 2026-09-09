#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_calibration_window_920fc.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("920fc", "lda"), ("9210c", "ld"),
                      ("9211c", "lda"), ("92128", "mov"),
                      ("92130", "stq"), ("92138", "mov"),
                      ("9213c", "st")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "window_word_0", "window_word_1", "window_word_2", "window_word_3",
        "control_address", "control_value", "publish_address", "completion_word")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "window.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_calibration_window_920fc
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.window_word_0, plan.window_word_1, plan.window_word_2,
            plan.window_word_3, plan.control_address, plan.control_value,
            plan.publish_address, plan.completion_word) == (
                0x403968, 0x4039f0, 0x850225, 0, 0x800010, 0x101, 0x804000, 6)

print("recovered geometry 0x920fc calibration-window fixture: ok")
