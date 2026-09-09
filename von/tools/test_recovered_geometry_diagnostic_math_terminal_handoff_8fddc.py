#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_diagnostic_math_terminal_handoff_8fddc.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("8fddc", "stq"), ("8fde4", "mov"),
                      ("8fde8", "st"), ("8fdf0", "mov")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())


class Input(ctypes.Structure):
    _fields_ = [("selected_window", ctypes.c_uint32 * 4)]


class Plan(ctypes.Structure):
    _fields_ = [("window_address", ctypes.c_uint32),
                ("window_word", ctypes.c_uint32 * 4),
                ("completion_word", ctypes.c_uint32),
                ("next_packet_entry", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "handoff.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_math_terminal_handoff_8fddc
    function.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    sample = Input((ctypes.c_uint32 * 4)(0x10, 0x20, 0x30, 0x40))
    plan = Plan()
    function(ctypes.byref(sample), ctypes.byref(plan))
    assert (plan.window_address, list(plan.window_word), plan.completion_word,
            plan.next_packet_entry) == (0x804000, [0x10, 0x20, 0x30, 0x40], 6, 0x8fdf0)

print("recovered geometry 0x8fddc terminal handoff fixture: ok")
