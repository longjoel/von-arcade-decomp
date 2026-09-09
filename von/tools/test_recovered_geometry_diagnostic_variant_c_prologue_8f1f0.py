#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_diagnostic_variant_c_prologue_8f1f0.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("8f1f0", "lda"), ("8f1f4", "stq"),
                      ("8f1f8", "ld")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())
assert "503b38" in listing[listing.index("8f1f0:"):listing.index("8f200:")]


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
    function = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_c_prologue_8f1f0
    function.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    sample = Input(0x87654321)
    plan = Plan()
    function(ctypes.byref(sample), ctypes.byref(plan))
    assert (plan.stack_adjust, plan.saved_register_address, plan.seed_address,
            plan.seed_word, plan.packet_entry) == (0x40, 0x70, 0x503b38,
                                                   0x87654321, 0x8f200)

print("recovered geometry 0x8f1f0 diagnostic-variant-C prologue fixture: ok")
