#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_diagnostic_variant_b_response_gate_8f0f8.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("8f0f4", "ld"), ("8f0fc", "cmpi"),
                      ("8f10c", "st"), ("8f114", "ld"),
                      ("8f11c", "bne")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())


class Input(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "persistent_seed", "frame_readback", "fifo_response")]


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "frame_readback", "published_address", "published_value", "fifo_address",
        "fifo_response", "selected_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "gate.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_b_response_gate_8f0f8
    function.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    sample = Input(0, 0x3000, 0xabcd1234)
    plan = Plan()
    function(ctypes.byref(sample), ctypes.byref(plan))
    assert (plan.frame_readback, plan.published_address, plan.published_value,
            plan.fifo_address, plan.fifo_response, plan.selected_target) == (
                0x3000, 0x801008, 0x3034, 0x884000, 0xabcd1234, 0x8f120)
    sample.persistent_seed = 1
    function(ctypes.byref(sample), ctypes.byref(plan))
    assert plan.selected_target == 0x8f174

print("recovered geometry 0x8f0f8 variant-B response fixture: ok")
