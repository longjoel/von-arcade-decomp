#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_diagnostic_variant_d_prefix_8f620.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("8f620", "ld"), ("8f628", "mov"),
                      ("8f62c", "st")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())
assert "503b38" in listing[listing.index("8f620:"):listing.index("8f634:")]


class Input(ctypes.Structure):
    _fields_ = [("persistent_seed", ctypes.c_uint32)]


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "seed_address", "seed_word", "first_fifo_word", "packet_body_entry")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "prefix.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_d_prefix_8f620
    function.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    sample = Input(0x0badcafe)
    plan = Plan()
    function(ctypes.byref(sample), ctypes.byref(plan))
    assert (plan.seed_address, plan.seed_word, plan.first_fifo_word,
            plan.packet_body_entry) == (0x503b38, 0x0badcafe, 5, 0x8f634)

print("recovered geometry 0x8f620 variant-D prefix fixture: ok")
