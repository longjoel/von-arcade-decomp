#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_batch_packet_8d400.c"

class Input(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "record_word", "record_word4", "parameter_word", "coordinate_2",
        "coordinate_0", "coordinate_4", "coordinate_6", "coordinate_8",
        "readback_word", "fifo_read_value")]

class Plan(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32 * 13), ("fifo_count", ctypes.c_uint32),
                ("control_address", ctypes.c_uint32), ("control_value", ctypes.c_uint32),
                ("window_word", ctypes.c_uint32 * 4),
                ("window_address", ctypes.c_uint32 * 4),
                ("completion_word", ctypes.c_uint32), ("readback_address", ctypes.c_uint32),
                ("fifo_read_address", ctypes.c_uint32), ("fifo_read_value", ctypes.c_uint32),
                ("publication_address", ctypes.c_uint32), ("publication_value", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "batch-packet.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_batch_packet_8d400
    function.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    sample = Input(0x11223344, 0x55667788, 0x12345678, 0xaaaa0002,
                   0xbbbb0001, 0xcccc0003, 0xdddd0004, 0xeeee0005,
                   0xeeee0005, 0x1234abcd)
    plan = Plan()
    function(ctypes.byref(sample), ctypes.byref(plan))
    assert list(plan.fifo_word) == [5, 47, 3, 4, 5, 22, 2, 21, 1, 20, 0x5678, 58, 0xeeee0005]
    assert plan.fifo_count == 13
    assert plan.control_address == 0x800010 and plan.control_value == 0x101
    assert list(plan.window_address) == [0x804000, 0x804004, 0x804008, 0x80400c]
    assert list(plan.window_word) == [0x11223344, 0x55667788, 4, 0]
    assert plan.completion_word == 6 and plan.readback_address == 0x802008
    assert plan.fifo_read_address == 0x884000 and plan.fifo_read_value == 0x1234abcd
    assert plan.publication_address == 0x801008 and plan.publication_value == 0xeeee0039

print("recovered geometry 0x8d400 batch-packet fixture: ok")
