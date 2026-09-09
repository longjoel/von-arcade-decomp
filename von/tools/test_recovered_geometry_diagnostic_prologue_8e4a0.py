#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_diagnostic_prologue_8e4a0.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("8e4a0", "lda"), ("8e4a4", "stq"),
                      ("8e4a8", "ld")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())
assert "503b38" in listing[listing.index("8e4a8:"):listing.index("8e4b0:")]


class Input(ctypes.Structure):
    _fields_ = [("persistent_seed", ctypes.c_uint32)]


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "stack_adjust", "saved_register_address", "seed_address", "seed_word",
        "packet_entry")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "prologue.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_prologue_8e4a0
    function.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    sample = Input(0xcafebabe)
    plan = Plan()
    function(ctypes.byref(sample), ctypes.byref(plan))
    assert (plan.stack_adjust, plan.saved_register_address, plan.seed_address,
            plan.seed_word, plan.packet_entry) == (0x50, 0x80, 0x503b38,
                                                   0xcafebabe, 0x8e4b0)

print("recovered geometry 0x8e4a0 diagnostic-prologue fixture: ok")
