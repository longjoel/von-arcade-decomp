#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_first_entry_gate_8dfc0.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("8dfc0", "cmpi"), ("8dfcc", "cmpibne"),
                      ("8e000", "shlo")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())

class Input(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in ("object_pointer", "object_count")]

class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in ("packet_body_admitted", "early_return")]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "gate.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    fn = ctypes.CDLL(str(library)).recovered_geometry_first_entry_gate_8dfc0
    fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    for sample, admitted in ((Input(0, 1), 0), (Input(1, 0), 0), (Input(1, 2), 1)):
        plan = Plan()
        fn(ctypes.byref(sample), ctypes.byref(plan))
        assert plan.packet_body_admitted == admitted
        assert plan.early_return == (0 if admitted else 1)
print("recovered geometry 0x8dfc0 entry gate: ok")
