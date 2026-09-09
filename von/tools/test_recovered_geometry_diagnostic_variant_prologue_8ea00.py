#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_diagnostic_variant_prologue_8ea00.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("8ea00", "lda"), ("8ea04", "stq"),
                      ("8ea08", "ld")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())
assert "503b38" in listing[listing.index("8ea00:"):listing.index("8ea10:")]


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
    function = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_prologue_8ea00
    function.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    sample = Input(0x12345678)
    plan = Plan()
    function(ctypes.byref(sample), ctypes.byref(plan))
    assert (plan.stack_adjust, plan.saved_register_address, plan.seed_address,
            plan.seed_word, plan.packet_entry) == (0x80, 0xb0, 0x503b38,
                                                   0x12345678, 0x8ea10)

print("recovered geometry 0x8ea00 diagnostic-variant prologue fixture: ok")
