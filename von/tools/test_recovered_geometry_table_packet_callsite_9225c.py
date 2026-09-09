#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_table_packet_callsite_9225c.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("9225c", "mov"), ("92294", "remi"),
                      ("922ac", "lda"), ("922f4", "ld"),
                      ("92318", "lda"), ("92320", "ld"),
                      ("92330", "lda"), ("92348", "st"),
                      ("92378", "st")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "source_value", "remainder", "frame_word", "frame_readback",
        *[f"fifo_word_{i}" for i in range(14)], "fifo_count", "table_base",
        "table_index", "response_word_0", "response_word_1", "response_word_2",
        "control_address", "control_value", "publish_address", "published",
        "completion_word")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "packet.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_table_packet_callsite_9225c
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(Plan)]
    response = (ctypes.c_uint32 * 3)(0x11111111, 0x22222222, 0x33333333)
    plan = Plan()
    function(61, 0xabcdef01, 0xdeadbeef, response, ctypes.byref(plan))
    assert (plan.remainder, plan.table_base, plan.table_index, plan.published,
            plan.control_address, plan.control_value, plan.publish_address,
            plan.completion_word) == (1, 0x2be52b0, 12, 1, 0x800010, 0x101,
                                      0x804000, 6)
    assert [getattr(plan, f"fifo_word_{i}") for i in range(14)] == [
        5, 18, 1, 0x40e00000, 0x41800000, 0xabcdef01, 21, 0xb800, 19,
        0x40400000, 0x40400000, 0x40400000, 58, 0xdeadbeef]
    response[0] = 0
    function(61, 0xabcdef01, 0xdeadbeef, response, ctypes.byref(plan))
    assert plan.published == 0

print("recovered geometry 0x9225c table-packet fixture: ok")
