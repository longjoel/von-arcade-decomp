"""Validate the 0x9ddac post-state dispatch/countdown gate."""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
source = ROOT / "von/i960/recovered_geometry_post_state_gate_9ddac.c"
library = pathlib.Path(tempfile.mkdtemp()) / "lib.so"
subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(source), "-o", str(library)], check=True)
lib = ctypes.CDLL(str(library))

class Plan(ctypes.Structure):
    _fields_ = [("fifo_address", ctypes.c_uint32), ("fifo_word_count", ctypes.c_uint32), ("fifo_word", ctypes.c_uint32), ("countdown", ctypes.c_int32 * 3), ("countdown_address", ctypes.c_uint32 * 3), ("frame_value", ctypes.c_uint32), ("gate_before", ctypes.c_uint32), ("gate_after", ctypes.c_uint32), ("startup_call", ctypes.c_uint32), ("startup_argument", ctypes.c_uint32)]

fn = lib.recovered_geometry_post_state_gate_plan
fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(Plan)]

def run(frame, gate, values):
    before = (ctypes.c_int32 * 3)(*values)
    plan = Plan()
    fn(frame, gate, before, ctypes.byref(plan))
    assert plan.fifo_address == 0x884000 and plan.fifo_word_count == 1 and plan.fifo_word == 6
    assert list(plan.countdown_address) == [0x562c9c, 0x562ca0, 0x562ca4]
    return plan

p = run(0x12345678, 9, [30, 30, 30])
assert p.gate_after == 0x12345678 and p.startup_call == 0
p = run(0x12345678, 0, [29, 30, 30])
assert p.gate_after == 0x12345678 and p.startup_call == 0
p = run(0x12345678, 0, [30, 30, 30])
assert p.gate_after == 1 and p.startup_call == 1 and p.startup_argument == 0x114c
print("PASS: 0x9ddac post-state gate")
