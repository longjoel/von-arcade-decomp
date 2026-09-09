#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_calibration_helper_handoff_9140c.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("9140c", "call"), ("91410", "lda"),
                      ("91418", "lda"), ("91420", "mov"),
                      ("91424", "call"), ("91428", "mov"),
                      ("9142c", "st")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "helper_target", "first_table_address", "second_table_address",
        "first_context_word", "second_context_word", "completion_word")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "handoff.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_calibration_helper_handoff_9140c
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
    plan = Plan()
    function(0x11223344, 0x55667788, ctypes.byref(plan))
    assert (plan.helper_target, plan.first_table_address, plan.second_table_address,
            plan.first_context_word, plan.second_context_word, plan.completion_word) == (
                0x8e310, 0x2be2cb4, 0x2be2d2c, 0x11223344, 0x55667788, 6)

print("recovered geometry 0x9140c calibration-helper handoff fixture: ok")
