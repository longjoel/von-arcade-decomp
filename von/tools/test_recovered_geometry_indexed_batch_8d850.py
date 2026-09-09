#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile
root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_indexed_batch_8d850.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (
    ("8d850", "ldos"), ("8d85c", "cmpibg"), ("8d884", "mulo"),
    ("8d8ac", "cmpibge"), ("8d8c0", "ld"), ("8da0c", "ldl"),
    ("8da08", "cmpobl"), ("8da20", "stl"), ("8da40", "cmpi"),
    ("8da4c", "bl"),
):
    assert any(address + ":" in line and text in line for line in listing.splitlines())
class I(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "source_m2", "source_0", "source_2", "source_4", "source_6",
        "selected_value_0", "record_word", "record_word_4", "record_word_8",
        "signed_count", "object_index", "index_bound", "readback_word", "record_active_word",
        "table_index", "selected_record_dword", "selected_record_word_8", "row_scale")]
class P(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32 * 13), ("fifo_count", ctypes.c_uint32),
                ("packet_emitted", ctypes.c_uint32), ("normalized_count", ctypes.c_uint32),
                ("adjusted_index", ctypes.c_uint32),
                ("table_byte_offset", ctypes.c_uint32), ("window_word", ctypes.c_uint32 * 4),
                ("window_address", ctypes.c_uint32 * 4), ("control_address", ctypes.c_uint32),
                ("control_value", ctypes.c_uint32), ("completion_word", ctypes.c_uint32),
                ("extended_record_count", ctypes.c_uint32), ("extended_record_stride", ctypes.c_uint32),
                ("source_start_offset", ctypes.c_uint32), ("destination_start_offset", ctypes.c_uint32),
                ("table_write", ctypes.c_uint32), ("table_address", ctypes.c_uint32),
                ("table_low_value", ctypes.c_uint32), ("table_high_value", ctypes.c_uint32)]
with tempfile.TemporaryDirectory() as d:
    so = pathlib.Path(d) / "batch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"), "-o", str(so), str(source)], check=True)
    f = ctypes.CDLL(str(so)).recovered_geometry_indexed_batch_8d850
    f.argtypes = [ctypes.POINTER(I), ctypes.POINTER(P)]
    i = I(0xfffe, 1, 2, 3, 4, 0x8001, 0x11111111, 0x22222222, 0x33333333, 2, 2, 9, 0x44444444, 1, 2, 0xaaaaaaaa, 0xbbbbbbbb, 4); p = P()
    f(ctypes.byref(i), ctypes.byref(p))
    assert list(p.fifo_word) == [5, 47, 0xfffe, 1, 2, 22, 3, 21, 4, 20, 0xffff8001, 58, 0x44444444]
    assert (p.normalized_count, p.adjusted_index, p.table_byte_offset) == (2, 1, 48)
    assert list(p.window_word) == [0x11111111, 0x22222222, 0x33333333, 0]
    assert (p.extended_record_count, p.extended_record_stride) == (2, 12)
    assert not p.table_write and p.table_address == 0x562448
    assert (p.table_low_value, p.table_high_value) == (0xaaaaaaaa, 0xbbbbbbbb)
    i.source_6 = 0x8002; i.row_scale = 3; f(ctypes.byref(i), ctypes.byref(p))
    assert p.fifo_word[8] == 0x8002 and p.table_byte_offset == 36
    i.signed_count = 0xffff; f(ctypes.byref(i), ctypes.byref(p)); assert p.extended_record_count == 1
    i.signed_count = 0; f(ctypes.byref(i), ctypes.byref(p)); assert not p.packet_emitted
    i.record_active_word = 0; i.table_index = 5; f(ctypes.byref(i), ctypes.byref(p)); assert p.table_write and p.table_address == 0x56246c
    i.table_index = 6; f(ctypes.byref(i), ctypes.byref(p)); assert not p.table_write
print("recovered geometry 0x8d850 indexed-batch fixtures: ok")
