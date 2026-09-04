#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_object_packet_8dd40.c"
names = ("coordinate_m2", "coordinate_0", "coordinate_2", "coordinate_4",
         "coordinate_6", "coordinate_8", "coordinate_10", "fifo_read_value",
         "object_word", "selected_word4", "selected_word8", "object_word_c",
         "output_low", "output_high", "frame_readback", "table_index")
class Input(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in names]
class Plan(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32 * 13), ("fifo_count", ctypes.c_uint32),
                ("fifo_read_address", ctypes.c_uint32), ("fifo_read_value", ctypes.c_uint32),
                ("control_address", ctypes.c_uint32), ("control_value", ctypes.c_uint32),
                ("window_address", ctypes.c_uint32 * 4), ("window_word", ctypes.c_uint32 * 4),
                ("completion_word", ctypes.c_uint32), ("selected_field_offset", ctypes.c_uint32),
                ("selected_field_value", ctypes.c_uint32), ("output_address_low", ctypes.c_uint32),
                ("output_address_high", ctypes.c_uint32), ("output_low", ctypes.c_uint32),
                ("output_high", ctypes.c_uint32), ("table_write", ctypes.c_uint32),
                ("table_address", ctypes.c_uint32)]
with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "object-packet.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    fn = ctypes.CDLL(str(library)).recovered_geometry_object_packet_8dd40
    fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    sample = Input(0xaaaa0001, 0xbbbb0002, 0xcccc0003, 0xdddd0004,
                   0xeeee0005, 0xffff0006, 0x11110007, 0,
                   0x12345678, 0x22222222, 0x33333333, 0x44444444,
                   0x55555555, 0x66666666, 0x77777777, 3)
    plan = Plan(); fn(ctypes.byref(sample), ctypes.byref(plan))
    assert list(plan.fifo_word) == [5, 47, 5, 6, 7, 22, 4, 21, 3, 20, 2, 58, 0x77777777]
    assert list(plan.window_word) == [0x12345678, 0x22222222, 0x44444444, 0]
    assert plan.selected_field_offset == 4 and plan.selected_field_value == 0x22222222
    assert plan.output_address_low == 0x174 and plan.output_address_high == 0x17c
    assert plan.table_write and plan.table_address == 0x562454
    sample.fifo_read_value = 1; fn(ctypes.byref(sample), ctypes.byref(plan))
    assert plan.selected_field_offset == 8 and plan.selected_field_value == 0x33333333
    assert plan.window_word[1] == 0x33333333
print("recovered geometry 0x8dd40 object-packet fixtures: ok")
