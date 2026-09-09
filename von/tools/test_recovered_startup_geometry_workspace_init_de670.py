#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_startup_geometry_workspace_init_de670.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("de678", "st"), ("de680", "stos"),
                      ("de688", "shlo"), ("de6d4", "st"),
                      ("de6e4", "ld"), ("de708", "st")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())

class Input(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("callback_marker", "status_halfword", "table_word")]

class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "field_504b90", "field_504b94", "field_504ba4", "field_504ba8",
        "field_504baa", "field_504bac", "field_504bae", "field_504bb0",
        "field_504bcc", "field_504bd0", "field_504bd4", "field_504bd8",
        "field_504bda")]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "workspace.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    fn = ctypes.CDLL(str(library)).recovered_startup_geometry_workspace_init_de670
    fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    plan = Plan()
    fn(ctypes.byref(Input(0x12345678, 0xabcdef01, 0xfeedface)), ctypes.byref(plan))
    assert plan.field_504b90 == 0xde630
    assert plan.field_504b94 == plan.field_504bac == plan.field_504bb0 == 0x5678
    assert plan.field_504ba8 == plan.field_504bae == 0x600
    assert plan.field_504baa == 0xef01
    assert plan.field_504ba4 == plan.field_504bd8 == plan.field_504bda == 0
    assert plan.field_504bcc == plan.field_504bd0 == 0x41d00000
    assert plan.field_504bd4 == 0xfeedface
print("recovered startup geometry 0xde670 workspace init: ok")
