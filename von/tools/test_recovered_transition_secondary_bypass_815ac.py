#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_secondary_bypass_815ac.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "current_state_504d68", "control_504dc8", "result_table",
        "initial_result", "result_destination", "control_one", "final_result",
        "status8_value", "tail_status_destination", "tail_status",
        "tail_selector_destination", "tail_selector", "tail_offset_destination",
        "tail_offset")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "secondary-bypass.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_transition_secondary_bypass_815ac
    build.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                      ctypes.POINTER(Plan)]

    plan = Plan()
    build(12, 0, 0x1111, ctypes.byref(plan))
    assert (plan.result_table, plan.initial_result, plan.final_result,
            plan.control_one) == (0x728A0, 0x1111, 0x1111, 0)

    build(12, 1, 0x2222, ctypes.byref(plan))
    assert (plan.initial_result, plan.final_result, plan.status8_value) == (0x2222, 8, 8)
    assert (plan.tail_status_destination, plan.tail_status,
            plan.tail_selector_destination, plan.tail_selector,
            plan.tail_offset_destination, plan.tail_offset) == (
        0x504DB8, 10, 0x504D9C, 2, 0x504DA0, 0x64)

print("recovered 0x815ac secondary-bypass vectors: ok")
