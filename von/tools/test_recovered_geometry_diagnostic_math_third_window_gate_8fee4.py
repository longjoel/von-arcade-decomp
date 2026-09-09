#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_diagnostic_math_third_window_gate_8fee4.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("8fee0", "cmpi"), ("8feec", "lda"),
                      ("8fef0", "st"), ("8fef8", "ld"),
                      ("8ff00", "bne")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())


class Input(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "state_flag", "frame_readback", "fifo_response")]


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "frame_readback", "published_address", "published_value", "fifo_address",
        "fifo_response", "selected_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "gate.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_math_third_window_gate_8fee4
    function.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    sample = Input(0, 0x9000, 0x55667788)
    plan = Plan()
    function(ctypes.byref(sample), ctypes.byref(plan))
    assert (plan.frame_readback, plan.published_address, plan.published_value,
            plan.fifo_address, plan.fifo_response, plan.selected_target) == (
                0x9000, 0x801008, 0x9034, 0x884000, 0x55667788, 0x8ff04)
    sample.state_flag = 1
    function(ctypes.byref(sample), ctypes.byref(plan))
    assert plan.selected_target == 0x8ff40

print("recovered geometry 0x8fee4 third-window gate fixture: ok")
