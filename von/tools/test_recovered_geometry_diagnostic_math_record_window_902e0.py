#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_diagnostic_math_record_window_902e0.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("902e0", "lda"), ("902f8", "lda"),
                      ("90308", "st"), ("90354", "stq"),
                      ("9035c", "mov"), ("90368", "mov"),
                      ("90378", "call")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "state_word", "window_word_0", "window_word_1", "window_word_2",
        "window_word_3", "zero_word_0", "zero_word_1", "zero_word_2",
        "nonzero_word_0", "nonzero_word_1", "nonzero_word_2", "control_address",
        "control_value", "publish_address", "completion_word_0",
        "completion_word_1", "completion_count", "call_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "window.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_math_record_window_902e0
    function.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
                         ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32,
                         ctypes.POINTER(Plan)]
    zero = (ctypes.c_uint32 * 3)(0x12d470, 0x12d4d4, 0xa8e93e)
    nonzero = (ctypes.c_uint32 * 3)(0x12d470, 0x5a3a46, 0xa8e93e)
    plan = Plan()
    function(0, zero, nonzero, 0xfeed, ctypes.byref(plan))
    assert (plan.window_word_0, plan.window_word_1, plan.window_word_2,
            plan.window_word_3, plan.completion_count, plan.call_target) == (
                0x12d470, 0x12d4d4, 0xa8e93e, 0, 2, 0x6fec0)
    function(1, zero, nonzero, 0xfeed, ctypes.byref(plan))
    assert (plan.window_word_1, plan.window_word_3) == (0x5a3a46, 0xfeed)

print("recovered geometry 0x902e0 record-window fixture: ok")
