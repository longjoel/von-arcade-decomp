#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_diagnostic_math_record_packet_901b0.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("901b0", "mov"), ("901c8", "lda"),
                      ("901d8", "movr"), ("901f8", "mov"),
                      ("90204", "ldos"), ("9020c", "setbit"),
                      ("90218", "mov"), ("90238", "st"),
                      ("90264", "mulr"), ("90290", "cvtzril"),
                      ("90294", "mov"), ("902ac", "st")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "source_halfword", "normalized_source", "shifted_source", "response_word",
        "computed_word", *[f"fifo_word_{i}" for i in range(14)], "fifo_count")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "packet.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_math_record_packet_901b0
    function.argtypes = [ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.POINTER(Plan)]
    plan = Plan()
    function(0x253 + 3, 0x11223344, 0xaabbccdd, ctypes.byref(plan))
    assert (plan.normalized_source, plan.shifted_source, plan.fifo_count) == (3, 0x180, 14)
    assert [getattr(plan, f"fifo_word_{i}") for i in range(14)] == [
        5, 18, 0x3f000000, 0x3f800000, 0xbfa66666, 21, 0x2012, 27,
        0x180, 27, 0x180, 20, 0xaabbccdd, 58]

print("recovered geometry 0x901b0 record-packet fixture: ok")
