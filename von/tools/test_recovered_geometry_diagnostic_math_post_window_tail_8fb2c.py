#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_diagnostic_math_post_window_tail_8fb2c.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("8fb2c", "bne"), ("8fb48", "st"),
                      ("8fbd0", "lda"), ("8fbdc", "cmpi"),
                      ("8fbf0", "ble")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())
assert "14292c" in listing[listing.index("8fbd0:"):listing.index("8fbf4:")]


class Input(ctypes.Structure):
    _fields_ = [("state_flag", ctypes.c_uint32),
                ("zero_window", ctypes.c_uint32 * 3),
                ("nonzero_window", ctypes.c_uint32 * 3),
                ("primary_cursor", ctypes.c_uint32),
                ("auxiliary_cursor", ctypes.c_uint32)]


class Plan(ctypes.Structure):
    _fields_ = [("selected_window", ctypes.c_uint32 * 4),
                ("control_address", ctypes.c_uint32),
                ("control_value", ctypes.c_uint32),
                ("completion_word", ctypes.c_uint32),
                ("next_primary_cursor", ctypes.c_uint32),
                ("next_auxiliary_cursor", ctypes.c_uint32),
                ("record_endpoint", ctypes.c_uint32),
                ("loop_continues", ctypes.c_uint32),
                ("continuation_entry", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "tail.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_math_post_window_tail_8fb2c
    function.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    zero = (ctypes.c_uint32 * 3)(7, 8, 9)
    nonzero = (ctypes.c_uint32 * 3)(10, 11, 12)
    sample = Input(0, zero, nonzero, 0x142900, 0x3000)
    plan = Plan()
    function(ctypes.byref(sample), ctypes.byref(plan))
    assert list(plan.selected_window) == [7, 8, 9, 0]
    assert (plan.control_address, plan.control_value, plan.completion_word,
            plan.next_primary_cursor, plan.next_auxiliary_cursor,
            plan.record_endpoint, plan.loop_continues, plan.continuation_entry) == (
                0x800010, 0x101, 6, 0x14292c, 0x302c, 0x14292c, 1, 0x8fa78)
    sample.state_flag = 1
    sample.primary_cursor = 0x142910
    function(ctypes.byref(sample), ctypes.byref(plan))
    assert list(plan.selected_window) == [10, 11, 12, 0] and not plan.loop_continues

print("recovered geometry 0x8fb2c post-window-tail fixture: ok")
