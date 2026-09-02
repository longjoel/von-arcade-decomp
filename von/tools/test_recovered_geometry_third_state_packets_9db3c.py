"""Validate the third 0x9db3c flagged/0x9dc64 clear geometry packets."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]

def load(source, function, struct_name):
    out = pathlib.Path(tempfile.mkdtemp()) / "lib.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(ROOT / "von/i960" / source), "-o", str(out)], check=True)
    lib = ctypes.CDLL(str(out))
    return lib, getattr(lib, function), getattr(__import__("builtins"), "object", object)

class Flagged(ctypes.Structure):
    _fields_ = [("flag_bit1", ctypes.c_uint32), ("state_word", ctypes.c_int16), ("masked_state_parameter", ctypes.c_uint32), ("derived_packet_word", ctypes.c_uint32), ("fifo_address", ctypes.c_uint32), ("fifo_word_count", ctypes.c_uint32), ("fifo_word", ctypes.c_uint32 * 13), ("board_readback_address", ctypes.c_uint32), ("published_pointer_address", ctypes.c_uint32), ("published_pointer_offset", ctypes.c_uint32), ("control_address", ctypes.c_uint32), ("control_value", ctypes.c_uint32), ("frame_publish_address", ctypes.c_uint32), ("frame_word", ctypes.c_uint32 * 2), ("frame_tail", ctypes.c_uint32 * 2), ("frame_value", ctypes.c_uint32)]

class Clear(ctypes.Structure):
    _fields_ = [("object_1e6", ctypes.c_int16), ("derived_packet_word", ctypes.c_uint32), ("fifo_address", ctypes.c_uint32), ("fifo_word_count", ctypes.c_uint32), ("fifo_word", ctypes.c_uint32 * 9), ("board_readback_address", ctypes.c_uint32), ("published_pointer_address", ctypes.c_uint32), ("published_pointer_offset", ctypes.c_uint32), ("object_flag_1df", ctypes.c_uint32), ("frame_value", ctypes.c_uint32), ("control_address", ctypes.c_uint32), ("control_value", ctypes.c_uint32), ("frame_publish_address", ctypes.c_uint32), ("frame_slot_offset", ctypes.c_uint32), ("frame_word", ctypes.c_uint32 * 2), ("frame_tail_offset", ctypes.c_uint32), ("frame_tail", ctypes.c_uint32 * 2), ("frame_variant", ctypes.c_uint32)]

lib, flagged, _ = load("recovered_geometry_third_flagged_state_packet_9db3c.c", "recovered_geometry_third_flagged_state_packet_plan", "Flagged")
flagged.argtypes = [ctypes.c_uint32, ctypes.c_int16, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Flagged)]
p = Flagged(); flagged(2, -1, 0x12345678, 0xabcdef01, 0x802008, ctypes.byref(p))
assert p.flag_bit1 == 1 and p.masked_state_parameter == 0xf000
assert list(p.fifo_word[:13]) == [29, 0xf000, 0x40400000, 19, 0x12345678, 0x42200000, 0x12345678, 0x3f800000, 18, 0x3f800000, 0, 0, 58]
q = Flagged(); flagged(0, 3, 0, 0, 0, ctypes.byref(q)); assert q.fifo_word_count == 0

lib, clear, _ = load("recovered_geometry_third_clear_flag_packet_9dc64.c", "recovered_geometry_third_clear_flag_packet_plan", "Clear")
clear.argtypes = [ctypes.c_int16, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Clear)]
r = Clear(); clear(-2, 0x89abcdef, 0, 0x10203040, 0x802008, ctypes.byref(r))
assert r.frame_slot_offset == 0x80 and r.frame_tail_offset == 0x88 and r.frame_word[1] == 0x40005c
s = Clear(); clear(7, 1, 1, 2, 3, ctypes.byref(s))
assert s.frame_slot_offset == 0x90 and s.frame_tail_offset == 0x98 and s.frame_word[1] == 0x40002c
print("PASS: 0x9db3c/0x9dc64 third state packets")
