#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_diagnostic_math_response_handoff_8f910.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("8f90c", "st"), ("8f914", "lda"),
                      ("8f918", "st"), ("8f920", "ld"),
                      ("8f928", "mov")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())


class Input(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in ("frame_readback", "fifo_response")]


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "frame_readback", "published_address", "published_value", "fifo_address",
        "fifo_response", "next_packet_entry")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "handoff.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_math_response_handoff_8f910
    function.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    sample = Input(0x55667788, 0x2468ace0)
    plan = Plan()
    function(ctypes.byref(sample), ctypes.byref(plan))
    assert (plan.frame_readback, plan.published_address, plan.published_value,
            plan.fifo_address, plan.fifo_response, plan.next_packet_entry) == (
                0x55667788, 0x801008, 0x556677bc, 0x884000, 0x2468ace0, 0x8f928)

print("recovered geometry 0x8f910 math-response handoff fixture: ok")
