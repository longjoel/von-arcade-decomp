#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_table_entry_gate_9224c.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("9224c", "ld"), ("92254", "lda"),
                      ("92258", "cmpobg"), ("9225c", "mov"),
                      ("92380", "subo")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "source_value", "threshold_value", "normal_target", "high_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "gate.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_table_entry_gate_9224c
    function.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]
    plan = Plan()
    function(0x12c, ctypes.byref(plan))
    assert (plan.source_value, plan.threshold_value, plan.normal_target,
            plan.high_target) == (0x12c, 0x12c, 0x9225c, 0x92380)
    function(0x12d, ctypes.byref(plan))
    assert plan.source_value == 0x12d

print("recovered geometry 0x9224c entry-gate fixture: ok")
