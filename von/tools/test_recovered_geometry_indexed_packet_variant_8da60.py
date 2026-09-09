#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile
root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_indexed_packet_variant_8da60.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (
    ("8da60", "ldos"), ("8da6c", "cmpibg"), ("8da94", "mulo"),
    ("8daac", "ble"), ("8db68", "ldl"), ("8db90", "ble"),
    ("8dd18", "addo"), ("8dd28", "bl"),
):
    assert any(address + ":" in line and text in line for line in listing.splitlines())

class I(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "value_0", "value_2", "value_4", "value_6", "value_8", "value_10",
        "record_dword_0", "record_word_8", "signed_count", "object_index", "index_bound", "row_scale")]
class P(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32 * 10), ("fifo_count", ctypes.c_uint32),
                ("packet_emitted", ctypes.c_uint32), ("xor_mask", ctypes.c_uint32),
                ("normalized_count", ctypes.c_uint32),
                ("adjusted_index", ctypes.c_uint32), ("table_byte_offset", ctypes.c_uint32),
                ("published_low", ctypes.c_uint32), ("published_high", ctypes.c_uint32),
                ("extended_record_count", ctypes.c_uint32), ("extended_record_stride", ctypes.c_uint32),
                ("extended_source_start_offset", ctypes.c_uint32),
                ("extended_destination_start_offset", ctypes.c_uint32)]
with tempfile.TemporaryDirectory() as d:
    so = pathlib.Path(d) / "variant.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"), "-o", str(so), str(source)], check=True)
    f = ctypes.CDLL(str(so)).recovered_geometry_indexed_packet_variant_8da60
    f.argtypes = [ctypes.POINTER(I), ctypes.POINTER(P)]
    i = I(1, 2, 3, 4, 5, 6, 0x11223344, 0x55667788, 2, 2, 9, 4); p = P()
    f(ctypes.byref(i), ctypes.byref(p))
    assert list(p.fifo_word) == [20, 0xffffffff, 21, 0xfffffffe, 22, 0xfffffffd, 58, 0x8004, 0x8005, 0x8006]
    assert (p.normalized_count, p.adjusted_index, p.table_byte_offset) == (2, 1, 48)
    assert (p.published_low, p.published_high) == (0x11223344, 0x55667788)
    assert (p.extended_record_count, p.extended_source_start_offset, p.extended_destination_start_offset) == (1, 12, 24)
    i.value_6 = 0x8002; i.row_scale = 3; f(ctypes.byref(i), ctypes.byref(p))
    assert p.fifo_word[7] == 0xffff0002 and p.table_byte_offset == 36
    i.signed_count = 1; f(ctypes.byref(i), ctypes.byref(p))
    assert p.extended_record_count == 0 and p.extended_destination_start_offset == 0
    i.signed_count = 0; f(ctypes.byref(i), ctypes.byref(p)); assert not p.packet_emitted
    i.object_index = 12; i.row_scale = 2; f(ctypes.byref(i), ctypes.byref(p))
    assert p.adjusted_index == 9 and p.table_byte_offset == 216
print("recovered geometry 0x8da60 indexed-packet variant fixtures: ok")
