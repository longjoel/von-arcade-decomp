#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_secondary_state2_812ac.c"

class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "control_504dc8", "flag_504e30", "result_table", "result_value",
        "result_destination", "status_destination", "published_status",
        "flag_bit2_set", "state_destination", "published_state", "state_target",
        "control_failure_target", "clear_bit_target", "target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "secondary-state2.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_transition_secondary_state2_812ac
    build.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                      ctypes.POINTER(Plan)]

    plan = Plan()
    build(1, 0, 0x1111, ctypes.byref(plan))
    assert (plan.result_destination, plan.status_destination,
            plan.published_status, plan.target) == (0x504D94, 0x504D94, 23, 0x8159C)

    build(1, 4, 0x2222, ctypes.byref(plan))
    assert (plan.flag_bit2_set, plan.state_destination,
            plan.published_state, plan.target) == (1, 0x504D98, 3, 0x815E0)

    build(0, 4, 0x3333, ctypes.byref(plan))
    assert (plan.result_destination, plan.status_destination,
            plan.published_status, plan.state_destination, plan.target) == (
        0x504D94, 0, 0, 0, 0x815E0)

print("recovered 0x812ac secondary-state2 vectors: ok")
