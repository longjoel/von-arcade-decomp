#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_secondary_state7_81528.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "control_504dc8", "object_state_64", "flag_504e30",
        "current_state_504d68", "result_table", "result_value",
        "result_destination", "initial_status", "final_state_destination",
        "published_state", "object_state3_match", "flag_bit2_set",
        "flag_bit1_set", "control_failure_target", "state3_target",
        "state2_target", "state1_target", "target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "secondary-state7.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_transition_secondary_state7_81528
    build.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                      ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]

    plan = Plan()
    build(1, 3, 0, 3, 0x1111, ctypes.byref(plan))
    assert (plan.initial_status, plan.published_state,
            plan.object_state3_match, plan.target) == (9, 3, 1, 0x815E0)

    build(1, 4, 6, 3, 0x2222, ctypes.byref(plan))
    assert (plan.flag_bit2_set, plan.flag_bit1_set,
            plan.published_state) == (1, 1, 3)

    build(1, 4, 2, 3, 0x3333, ctypes.byref(plan))
    assert plan.published_state == 2

    build(1, 4, 0, 3, 0x4444, ctypes.byref(plan))
    assert plan.published_state == 1

    build(0, 3, 4, 3, 0x5555, ctypes.byref(plan))
    assert (plan.final_state_destination, plan.published_state,
            plan.target) == (0, 0, 0x815E0)

print("recovered 0x81528 secondary-state7 vectors: ok")
