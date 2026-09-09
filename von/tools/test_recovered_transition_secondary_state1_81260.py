#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_secondary_state1_81260.c"

class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "related_state_first", "related_state_second", "control_504dc8",
        "result_table", "result_value", "result_destination", "selector_value",
        "first_state6_target", "state4_target", "control_failure_target",
        "second_state6_target", "common_target", "target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "secondary-state1.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_transition_secondary_state1_81260
    build.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                      ctypes.c_uint32, ctypes.POINTER(Plan)]

    plan = Plan()
    build(6, 6, 1, 0x1111, ctypes.byref(plan))
    assert (plan.result_destination, plan.target) == (0, 0x81414)

    build(4, 4, 1, 0x2222, ctypes.byref(plan))
    assert (plan.selector_value, plan.result_destination, plan.target) == (
        7, 0, 0x815D8)

    build(3, 3, 0, 0x3333, ctypes.byref(plan))
    assert (plan.result_destination, plan.target) == (0x504D94, 0x815E0)

    build(3, 6, 1, 0x4444, ctypes.byref(plan))
    assert plan.target == 0x81470
    build(3, 3, 1, 0x5555, ctypes.byref(plan))
    assert plan.target == 0x815D4

print("recovered 0x81260 secondary-state1 vectors: ok")
