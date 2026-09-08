#!/usr/bin/env python3
"""Validate the exact entry gate for the 0x7a9f0 transition route."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_route_7a9f0.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "initial_state_504db8", "route", "calls_timing_variant",
        "timing_target", "packet_threshold", "record_selector", "table_base",
        "packet_target", "related_field_offset")]


with tempfile.TemporaryDirectory(prefix="von-transition-route-") as directory:
    library = pathlib.Path(directory) / "transition-route.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_route_7a9f0
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.POINTER(Plan)]
    function.restype = None

    def plan(selector, timing):
        result = Plan()
        function(selector, timing, ctypes.byref(result))
        return result

    for selector in (0, 1, 0x1234, 0xfffffffe):
        for timing in (0, 99):
            result = plan(selector, timing)
            assert (result.route, result.calls_timing_variant) == (0, 1)

    # The sentinel suppresses packet work even above the threshold.
    result = plan(0xffffffff, 0xffffffff)
    assert (result.route, result.calls_timing_variant) == (0, 1)

    for selector in (0, 1, 0x1234, 0xfffffffe):
        result = plan(selector, 100)
        assert (result.route, result.calls_timing_variant) == (1, 0)

    result = plan(7, 100)
    assert (result.initial_state_504db8, result.timing_target,
            result.packet_threshold, result.record_selector,
            result.table_base, result.packet_target,
            result.related_field_offset) == (10, 0x786d0, 99, 7, 0x505060,
                                             0x7aa30, 0x74)

print("PASS: 0x7a9f0 transition-route entry gate vectors")
