#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_match_geometry_state_gate_76b00.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("76b0c", "cmpi"), ("76b20", "cmpibe"),
                      ("76b30", "cmpibne"), ("76b7c", "bbc"),
                      ("76b98", "ld")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())

class Input(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("current_state", "related_class", "related_state", "global_bit6_set")]

class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("early_return_state9", "class_19_or_20", "state6_arm",
                 "bit6_publication_arm", "related_state3_arm")]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "state-gate.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    fn = ctypes.CDLL(str(library)).recovered_match_geometry_state_gate_76b00
    fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    plan = Plan()
    fn(ctypes.byref(Input(9, 19, 3, 0)), ctypes.byref(plan))
    assert (plan.early_return_state9, plan.class_19_or_20, plan.state6_arm,
            plan.bit6_publication_arm, plan.related_state3_arm) == (1, 1, 0, 1, 1)
    fn(ctypes.byref(Input(6, 20, 2, 1)), ctypes.byref(plan))
    assert (plan.early_return_state9, plan.class_19_or_20, plan.state6_arm,
            plan.bit6_publication_arm, plan.related_state3_arm) == (0, 1, 1, 0, 0)
    fn(ctypes.byref(Input(4, 18, 3, 0)), ctypes.byref(plan))
    assert (plan.class_19_or_20, plan.state6_arm, plan.related_state3_arm) == (0, 0, 1)
print("recovered match geometry 0x76b00 state gate: ok")
