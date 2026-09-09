#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile
root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_indexed_packet_8d5d0.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, instruction in (
    ("8d5dc", r"cmpibg\tg4,g2,0x8d5e4"),
    ("8d5e0", r"subo\t1,g4,g2"),
    ("8d604", r"mulo\tg6,g4,g4"),
    ("8d610", r"cmpi\t0,g5"),
    ("8d6e8", r"ble\t0x8d848"),
    ("8d6f8", r"shlo\t1,g0,g4"),
    ("8d6fc", r"addo\tg0,g4,g4"),
    ("8d704", r"ld\t(g3),g4"),
    ("8d844", r"bg\t0x8d704"),
):
    instruction_text = instruction.replace(r"\t", " ")
    assert any(address + ":" in line and instruction_text in line.replace("\t", " ")
               for line in listing.splitlines())
class I(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in ("value_0", "value_2", "value_4", "value_6", "value_8", "value_10", "signed_count", "object_index", "index_bound", "row_scale")]
class P(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32 * 10), ("fifo_count", ctypes.c_uint32), ("xor_mask", ctypes.c_uint32), ("normalized_count", ctypes.c_uint32), ("next_record_offset", ctypes.c_uint32), ("extended_records_enabled", ctypes.c_uint32), ("adjusted_index", ctypes.c_uint32), ("table_byte_offset", ctypes.c_uint32), ("extended_record_count", ctypes.c_uint32), ("extended_record_stride", ctypes.c_uint32), ("extended_source_start_offset", ctypes.c_uint32), ("extended_destination_start_offset", ctypes.c_uint32)]
with tempfile.TemporaryDirectory() as d:
    so = pathlib.Path(d) / "indexed.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"), "-o", str(so), str(source)], check=True)
    f = ctypes.CDLL(str(so)).recovered_geometry_indexed_packet_8d5d0
    f.argtypes = [ctypes.POINTER(I), ctypes.POINTER(P)]
    p = P(); i = I(1, 2, 3, 4, 5, 6, 0xffff, 2, 9, 4); f(ctypes.byref(i), ctypes.byref(p))
    assert list(p.fifo_word) == [20, 0xffffffff, 21, 0xfffffffe,
                                 22, 0xfffffffd, 47, 0x8004, 0x8005, 0x8006]
    assert p.fifo_count == 10 and p.xor_mask == 0x8000 and p.normalized_count == 1 and not p.extended_records_enabled and p.next_record_offset == 12
    assert p.adjusted_index == 1 and p.table_byte_offset == 48
    i.value_6 = 0x8002; i.row_scale = 3; f(ctypes.byref(i), ctypes.byref(p))
    assert p.fifo_word[7] == 0xffff0002 and p.table_byte_offset == 36
    i.value_6 = 4; i.row_scale = 4
    assert p.extended_record_count == 0 and p.extended_record_stride == 12
    assert p.extended_source_start_offset == 0 and p.extended_destination_start_offset == 0
    i.signed_count = 1; f(ctypes.byref(i), ctypes.byref(p)); assert p.xor_mask == 0x8000 and p.normalized_count == 1 and not p.extended_records_enabled and p.fifo_word[7] == 0x8004
    i.signed_count = 2; f(ctypes.byref(i), ctypes.byref(p)); assert p.xor_mask == 0x8000 and p.normalized_count == 2 and p.extended_records_enabled and p.fifo_word[7] == 0x8004
    assert p.extended_record_count == 1 and p.extended_source_start_offset == 12 and p.extended_destination_start_offset == 24
    i.signed_count = 0xfffc; f(ctypes.byref(i), ctypes.byref(p)); assert p.normalized_count == 4 and p.extended_records_enabled
    assert p.extended_record_count == 3 and p.extended_source_start_offset == 12 and p.extended_destination_start_offset == 48
    i = I(1, 2, 3, 0xffff, 0x8000, 0x7fff, 1, 2, 9, 0xffff)
    f(ctypes.byref(i), ctypes.byref(p))
    assert list(p.fifo_word[1:6:2]) == [0xffffffff, 0xfffffffe, 0xfffffffd]
    assert list(p.fifo_word[7:10]) == [0xffff7fff, 0xffff0000, 0x00007fff ^ 0x8000]
    assert p.adjusted_index == 1 and p.table_byte_offset == 0xfffffff4
    i.object_index = 12; i.value_6 = 2; i.row_scale = 2; i.index_bound = 9; f(ctypes.byref(i), ctypes.byref(p))
    assert p.adjusted_index == 9 and p.table_byte_offset == 216
print("recovered geometry 0x8d5d0 indexed-packet fixtures: ok")
