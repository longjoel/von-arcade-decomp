#!/usr/bin/env python3
"""Validate the 0x7bf10 sentinel/state dispatch prefix."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_route_7bf10.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "route", "calls_timing_variant", "timing_target", "packet_target",
        "writes_504d84", "value_504d84", "packet_table_base",
        "selector", "object_state_offset", "related_pointer_offset")]


with tempfile.TemporaryDirectory(prefix="von-transition-route-7bf10-") as directory:
    library = pathlib.Path(directory) / "transition-route-7bf10.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_route_7bf10
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.POINTER(Plan)]
    function.restype = None

    def plan(selector, state):
        result = Plan()
        function(selector, state, ctypes.byref(result))
        return result

    for state in range(16):
        result = plan(0xffffffff, state)
        assert (result.route, result.calls_timing_variant,
                result.timing_target, result.writes_504d84,
                result.value_504d84) == (
            0, 1, 0x78740 if state in (2, 7) else 0x786d0, 1, 1)

    for selector in (0, 1, 0x1234, 0xfffffffe):
        result = plan(selector, 7)
        assert (result.route, result.calls_timing_variant,
                result.timing_target, result.writes_504d84) == (1, 0, 0, 0)
        assert result.selector == selector

    result = plan(0xffffffff, 2)
    assert (result.packet_target, result.packet_table_base,
            result.object_state_offset, result.related_pointer_offset) == \
        (0x7bf58, 0x505060, 0x64, 0x74)

print("PASS: 0x7bf10 transition-route dispatch vectors")
