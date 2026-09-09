#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_first_packet_8e000.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("8e014", "cmpi"), ("8e030", "st"),
                      ("8e0e0", "ldl"), ("8e10c", "ble"),
                      ("8e110", "addo"), ("8e114", "addo"),
                      ("8e118", "addo"), ("8e11c", "addo")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())

class Input(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "value_0", "value_2", "value_4", "value_6", "value_8", "value_10",
        "table_pair_low", "table_pair_high", "signed_count")]

class Plan(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32 * 11), ("fifo_count", ctypes.c_uint32),
                ("xor_mask", ctypes.c_uint32), ("normalized_count", ctypes.c_uint32),
                ("object_field_24c", ctypes.c_uint32),
                ("extended_records_enabled", ctypes.c_uint32),
                ("next_record_stride", ctypes.c_uint32),
                ("continuation_record_count", ctypes.c_uint32),
                ("continuation_record_stride", ctypes.c_uint32),
                ("continuation_source_start_offset", ctypes.c_uint32),
                ("continuation_table_start_offset", ctypes.c_uint32),
                ("continuation_aux_start_offset", ctypes.c_uint32),
                ("continuation_destination_base_offset", ctypes.c_uint32),
                ("table_low_address", ctypes.c_uint32),
                ("table_high_address", ctypes.c_uint32),
                ("table_pair_low", ctypes.c_uint32),
                ("table_pair_high", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "first.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    fn = ctypes.CDLL(str(library)).recovered_geometry_first_packet_8e000
    fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    sample = Input(1, 0x8000, 3, 0xffff, 0x8001, 0x7fff,
                   0x11223344, 0x55667788, 0xfffc)
    plan = Plan(); fn(ctypes.byref(sample), ctypes.byref(plan))
    assert list(plan.fifo_word) == [20, 0xffffffff, 21, 0x8000, 22, 0xfffffffd,
                                    46, 0xffff7fff, 0xffff0001, 0xffff, 58]
    assert plan.fifo_count == 11 and plan.xor_mask == 0x8000
    assert plan.normalized_count == 4 and plan.object_field_24c == 4 and plan.extended_records_enabled
    assert plan.next_record_stride == 12
    assert (plan.continuation_record_count, plan.continuation_record_stride) == (3, 12)
    assert (plan.continuation_source_start_offset, plan.continuation_table_start_offset,
            plan.continuation_aux_start_offset, plan.continuation_destination_base_offset) == (8, 12, 2, 8)
    assert (plan.table_low_address, plan.table_high_address,
            plan.table_pair_low, plan.table_pair_high) == (
        0x562480, 0x562488, 0x11223344, 0x55667788)
    sample.signed_count = 1; fn(ctypes.byref(sample), ctypes.byref(plan))
    assert plan.normalized_count == 1 and plan.object_field_24c == 1 and not plan.extended_records_enabled
    assert plan.continuation_record_count == 0 and plan.continuation_source_start_offset == 0
print("recovered geometry 0x8e000 first-packet fixture: ok")
