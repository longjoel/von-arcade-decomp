#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_inner_continuation_tail_8e2b0.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("8e2b0", "b"), ("8e2dc", "addo"),
                      ("8e2e4", "addo"), ("8e2f8", "bg"), ("8e2fc", "mov")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())


class Input(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "table_arm_active", "table_index", "selected_record_dword",
        "selected_record_word_8", "table_cursor", "auxiliary_cursor",
        "source_cursor", "destination_cursor", "record_counter",
        "object_cursor", "destination_record_cursor", "record_limit")]


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "table_write", "table_address", "table_low_value", "table_high_value",
        "next_table_cursor", "next_auxiliary_cursor", "next_source_cursor",
        "next_destination_cursor", "next_record_counter", "next_object_cursor",
        "next_destination_record_cursor", "continuation_taken", "continuation_entry")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "tail.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_inner_continuation_tail_8e2b0
    function.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    sample = Input(1, 4, 0x11223344, 0x55667788, 0x1000, 0x2000,
                   0x3000, 0x4000, 2, 0x5000, 0x6000, 5)
    plan = Plan()
    function(ctypes.byref(sample), ctypes.byref(plan))
    assert (plan.table_write, plan.table_address, plan.table_low_value,
            plan.table_high_value) == (1, 0x562460, 0x11223344, 0x55667788)
    assert (plan.next_table_cursor, plan.next_auxiliary_cursor,
            plan.next_source_cursor, plan.next_destination_cursor) == (0x100c, 0x2002, 0x300c, 0x400c)
    assert (plan.next_record_counter, plan.next_object_cursor,
            plan.next_destination_record_cursor, plan.continuation_taken,
            plan.continuation_entry) == (3, 0x5008, 0x600c, 1, 0x8e120)
    sample.table_index = 6
    sample.record_counter = 5
    function(ctypes.byref(sample), ctypes.byref(plan))
    assert not plan.table_write and not plan.continuation_taken

print("recovered geometry 0x8e2b0 continuation-tail fixture: ok")
