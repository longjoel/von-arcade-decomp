#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_diagnostic_variant_window_tail_8ebb8.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("8ebb8", "lda"), ("8ebcc", "st"),
                      ("8ebd4", "lda"), ("8ebd8", "ble")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())
assert "142354" in listing[listing.index("8ebb8:"):listing.index("8ebdc:")]


class Input(ctypes.Structure):
    _fields_ = [("persistent_seed", ctypes.c_uint32),
                ("zero_window", ctypes.c_uint32 * 3),
                ("nonzero_window", ctypes.c_uint32 * 3),
                ("primary_cursor", ctypes.c_uint32),
                ("secondary_cursor", ctypes.c_uint32)]


class Plan(ctypes.Structure):
    _fields_ = [("selected_window", ctypes.c_uint32 * 4),
                ("control_address", ctypes.c_uint32),
                ("control_value", ctypes.c_uint32),
                ("completion_word", ctypes.c_uint32),
                ("next_primary_cursor", ctypes.c_uint32),
                ("next_secondary_cursor", ctypes.c_uint32),
                ("record_endpoint", ctypes.c_uint32),
                ("loop_continues", ctypes.c_uint32),
                ("continuation_entry", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "tail.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_window_tail_8ebb8
    function.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    zero = (ctypes.c_uint32 * 3)(1, 2, 3)
    nonzero = (ctypes.c_uint32 * 3)(4, 5, 6)
    sample = Input(0, zero, nonzero, 0x142300, 0x2000)
    plan = Plan()
    function(ctypes.byref(sample), ctypes.byref(plan))
    assert list(plan.selected_window) == [1, 2, 3, 0]
    assert (plan.control_address, plan.control_value, plan.completion_word,
            plan.next_primary_cursor, plan.next_secondary_cursor,
            plan.record_endpoint, plan.loop_continues, plan.continuation_entry) == (
                0x800010, 0x101, 6, 0x14232c, 0x202c, 0x142354, 1, 0x8ea60)
    sample.persistent_seed = 1
    sample.primary_cursor = 0x142340
    function(ctypes.byref(sample), ctypes.byref(plan))
    assert list(plan.selected_window) == [4, 5, 6, 0] and not plan.loop_continues

print("recovered geometry 0x8ebb8 variant-window-tail fixture: ok")
