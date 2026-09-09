#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_secondary_state5_fallback_81440.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "control_504dc8", "object_state_64", "current_state_504d68",
        "result_table", "result_value", "result_destination",
        "published_status", "status_destination", "state6_status_target",
        "normal_target", "control_failure_target", "target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "secondary-state5-fallback.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_transition_secondary_state5_fallback_81440
    build.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                      ctypes.c_uint32, ctypes.POINTER(Plan)]

    plan = Plan()
    build(1, 6, 3, 0x1111, ctypes.byref(plan))
    assert (plan.result_table, plan.status_destination,
            plan.published_status, plan.target) == (0x728A0, 0x504D94, 9, 0x815E0)

    build(1, 4, 3, 0x2222, ctypes.byref(plan))
    assert (plan.status_destination, plan.published_status,
            plan.target) == (0, 0, 0x815D4)

    build(0, 6, 3, 0x3333, ctypes.byref(plan))
    assert (plan.status_destination, plan.published_status,
            plan.target) == (0, 0, 0x815E0)

print("recovered 0x81440 state5-fallback vectors: ok")
