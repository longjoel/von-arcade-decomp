#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_table_packet_callsite_92380.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("92380", "subo"), ("92384", "cmpobg"),
                      ("923c0", "remi"), ("923d8", "shlo"),
                      ("9241c", "ld"), ("9244c", "lda"),
                      ("92454", "ld"), ("92440", "lda"),
                      ("924a0", "mov")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "source_value", "adjusted_value", "remainder", "frame_word", "frame_readback",
        *[f"fifo_word_{i}" for i in range(14)], "fifo_count", "table_base",
        "table_index", "response_word_0", "response_word_1", "response_word_2",
        "control_address", "control_value", "publish_address", "published",
        "completion_word")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "packet.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_table_packet_callsite_92380
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(Plan)]
    response = (ctypes.c_uint32 * 3)(1, 2, 3)
    plan = Plan()
    function(45, 0xabcdef01, 0xdeadbeef, response, ctypes.byref(plan))
    assert (plan.adjusted_value, plan.remainder, plan.table_index, plan.published,
            plan.fifo_count, plan.fifo_word_0, plan.fifo_word_6,
            plan.fifo_word_12) == (30, 0, 0, 1, 13, 5, 0xc000, 0xdeadbeef)
    assert [getattr(plan, f"fifo_word_{i}") for i in range(13)] == [
        5, 18, 0x40e00000, 0x41800000, 0xabcdef01, 21, 0xc000, 19,
        0x40400000, 0x40400000, 0x40400000, 58, 0xdeadbeef]

print("recovered geometry 0x92380 table-packet fixture: ok")
