#!/usr/bin/env python3
"""Check the 0x7e950 status table and action-30 tail."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_geometry_status_dispatch_7e950.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("original_status", "normalized_index", "table_target",
                 "published_status", "control_504da4", "calls_79050",
                 "action_destination", "action_value", "status_destination")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-geometry-status-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_geometry_status_dispatch_7e950
    function.argtypes = [ctypes.c_uint32] * 2 + [ctypes.POINTER(Plan)]
    function.restype = None

    expected_targets = [0x7e99c, 0x7e9b4, 0x7e9bc, 0x7e9c4,
                        0x7e9c8, 0x7e9c8, 0x7e9c8, 0x7e9c8,
                        0x7e9c8, 0x7e9c8, 0x7e9a4, 0x7e9ac]
    expected_status = [1, 2, 3, 4, 12, 13, 14, 15, 16, 17, 2, 3]
    for index, (target, status) in enumerate(zip(expected_targets, expected_status)):
        plan = Plan()
        function(index + 8, 1, ctypes.byref(plan))
        assert (plan.normalized_index, plan.table_target,
                plan.published_status, plan.calls_79050) == (index, target, status, 1)

    plan = Plan()
    function(19, 0, ctypes.byref(plan))
    assert (plan.normalized_index, plan.table_target, plan.published_status,
            plan.calls_79050) == (11, 0x7e9ac, 3, 0)
    plan = Plan()
    function(7, 0, ctypes.byref(plan))
    assert plan.normalized_index == 0xffffffff
    assert (plan.table_target, plan.published_status) == (0x7e9c8, 7)

print("recovered 0x7e950 status-dispatch vectors: ok")
