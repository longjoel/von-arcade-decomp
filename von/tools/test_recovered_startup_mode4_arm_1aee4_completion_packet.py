#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "phase_latch", "fifo_address", "fifo_word_count")]
    _fields_ += [("fifo_word", ctypes.c_uint32 * 13)]
    _fields_ += [(n, ctypes.c_uint32) for n in ("register_r27", "derived_command", "frame_publish_address")]
    _fields_ += [("frame_word", ctypes.c_uint32 * 4)]
    _fields_ += [(n, ctypes.c_uint32) for n in (
        "control_address", "control_value", "pointer_source_address", "pointer_value",
        "pointer_destination", "pointer_destination_value", "packet_emitted", "return_target")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-1aee4-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_1aee4_completion_packet.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_1aee4_completion_packet
    fn.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Result)]
    out = Result()
    fn(0, 7, 0x802008, ctypes.byref(out))
    assert (out.packet_emitted, out.fifo_word_count, out.return_target) == (0, 13, 0x1afd0)
    fn(1, 7, 0x12345678, ctypes.byref(out))
    assert list(out.fifo_word) == [5, 16, 18, 0, 0, 0x3dcccccd, 19, 0x41a00000, 0x41a00000, 0x3f800000, 38, 0x12345678, 6]
    assert (list(out.frame_word), out.frame_publish_address, out.control_address, out.control_value, out.pointer_destination, out.pointer_destination_value, out.derived_command) == ([0, 0x400128, 0x8f31a0, 0], 0x804000, 0x800010, 0x101, 0x801008, 0x123456ac, 38)
    fn(1, 0xffffffff, 0, ctypes.byref(out))
    assert out.fifo_word[10] == 30
print("PASS: 0x1aee4 slot-10 completion packet")
