#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_calibration_secondary_math_handoff_92010.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("92010", "call"), ("92014", "lda"),
                      ("9201c", "lda"), ("92028", "call"),
                      ("9202c", "ldl"), ("92034", "addr"),
                      ("92040", "lda"), ("9206c", "subrl"),
                      ("92070", "mov")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "helper_target", "first_table_address", "second_table_address",
        "helper_context", "response_word", "source_sum", "first_multiplier",
        "first_bias", "second_multiplier", "second_bias", "next_packet_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "handoff.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_calibration_secondary_math_handoff_92010
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.POINTER(Plan)]
    plan = Plan()
    function(0x1234, 0x5678, 0x9abc, ctypes.byref(plan))
    assert (plan.helper_target, plan.first_table_address, plan.second_table_address,
            plan.helper_context, plan.response_word, plan.source_sum,
            plan.first_multiplier, plan.first_bias, plan.second_multiplier,
            plan.second_bias, plan.next_packet_target) == (
                0x8e310, 0x2be2cb4, 0x2be2d2c, 0x1234, 0x5678, 0x9abc,
                0xcccccccd, 0x3feccccc, 0xcccccccd, 0x400ccccc, 0x92070)

print("recovered geometry 0x92010 calibration-math handoff fixture: ok")
