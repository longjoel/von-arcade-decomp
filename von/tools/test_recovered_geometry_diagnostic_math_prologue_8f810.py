#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_diagnostic_math_prologue_8f810.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("8f810", "lda"), ("8f814", "stq"),
                      ("8f818", "st"), ("8f81c", "ld")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())
assert "503b38" in listing[listing.index("8f81c:"):listing.index("8f824:")]
assert "562b40" in listing[listing.index("8f824:"):listing.index("8f82c:")]


class Input(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in ("persistent_seed", "saved_g12")]


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "stack_adjust", "saved_register_address", "saved_g12_address", "saved_g12",
        "seed_address", "seed_word", "source_address", "source_entry")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "prologue.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_math_prologue_8f810
    function.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    sample = Input(0xabcdef01, 0x10203040)
    plan = Plan()
    function(ctypes.byref(sample), ctypes.byref(plan))
    assert (plan.stack_adjust, plan.saved_register_address, plan.saved_g12_address,
            plan.saved_g12, plan.seed_address, plan.seed_word,
            plan.source_address, plan.source_entry) == (
                0xc0, 0xe0, 0xf0, 0x10203040, 0x503b38, 0xabcdef01,
                0x562b40, 0x8f824)

print("recovered geometry 0x8f810 diagnostic-math prologue fixture: ok")
