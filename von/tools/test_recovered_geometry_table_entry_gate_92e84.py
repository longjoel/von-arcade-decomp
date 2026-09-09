#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_table_entry_gate_92e84.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("92e84", "ld"), ("92e8c", "shlo"),
                      ("92e90", "lda"), ("92e98", "cmpobg")):
    assert any(address + ":" in line and text in line
               for line in listing.splitlines())


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "source_value", "threshold_value", "adjusted_value",
        "selected_target", "packet_target", "fallback_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "gate.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I",
                    str(root / "von/i960"), "-o", str(library),
                    str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_table_entry_gate_92e84
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.POINTER(Plan)]
    plan = Plan()
    function(0x5624b8, 180, ctypes.byref(plan))
    assert (plan.threshold_value, plan.adjusted_value,
            plan.selected_target, plan.packet_target,
            plan.fallback_target) == (120, 120, 0x92e9c, 0x92e9c, 0x92fc0)
    function(0x5624b8, 181, ctypes.byref(plan))
    assert (plan.adjusted_value, plan.selected_target) == (121, 0x92fc0)
    function(0x5624b8, 0x3b, ctypes.byref(plan))
    assert (plan.adjusted_value, plan.selected_target) == (0xffffffff, 0x92fc0)

print("recovered geometry 0x92e84 threshold-entry fixture: ok")
