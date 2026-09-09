#!/usr/bin/env python3
"""Validate the bounded state-update slice at i960 0x3540."""
import ctypes
import pathlib
import subprocess
import tempfile


class Step(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("cleared_status_byte", "bit3_set", "next_state")]


root = pathlib.Path(__file__).parents[2]
with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "step.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(root / "von/i960/recovered_input_state_step_3540.c"),
                    "-o", str(so)], check=True)
    fn = ctypes.CDLL(str(so)).recovered_input_state_step_3540
    fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Step)]
    for state in (0, 1, 14, 15, 16, 0xFFFFFFFF):
        for status, expected in ((0x00, 0), (0x08, state + 1 if state <= 15 else state)):
            result = Step()
            fn(state, status, ctypes.byref(result))
            actual = (result.cleared_status_byte, result.bit3_set,
                      result.next_state)
            wanted = (1, 1 if status & 8 else 0, expected)
            if actual != wanted:
                raise SystemExit("0x3540 state-step mismatch")

print("PASS: 0x3540 input state step")


class Followup(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "admission_passed", "timing_counter_incremented", "status_field_checked",
        "prior_field38", "field38_next", "field38_incremented", "field38_reset_to_nine",
        "field3c_incremented", "field_c4_cleared", "table_copy_called",
        "special_ready", "special_helper_called", "special_helper_argument",
        "status_f2_published", "field_c6_cleared")]

with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "step-followup.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(root / "von/i960/recovered_input_state_step_3540.c"),
                    "-o", str(so)], check=True)
    fn = ctypes.CDLL(str(so)).recovered_input_state_followup_3540
    fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Followup)]
    for args, expected in (
        ((6, 0x3ff, 0, 8), (1, 1, 1, 8, 9, 1, 1, 0, 1, 1, 0, 0, 0x111b, 0, 0)),
        ((6, 0x400, 0, 8), (0, 0, 0, 8, 8, 0, 0, 0, 0, 0, 0, 0, 0x111b, 0, 0)),
        ((6, 0, 0, 9), (1, 1, 1, 9, 9, 1, 1, 0, 1, 1, 1, 1, 0x111b, 1, 1)),
        ((5, 0, 0, 9), (0, 0, 0, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0x111b, 0, 0)),
    ):
        result = Followup()
        fn(*args, ctypes.byref(result))
        actual = tuple(getattr(result, name) for name, _ in Followup._fields_)
        assert actual == expected, (args, actual, expected)

print("PASS: 0x3584 input-state followup")


class CounterGate(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "status482_bit0_set", "c2_limit_passed", "c2_incremented",
        "c2_cleared", "c2_nonzero_checked", "status480_bit0_checked",
        "status480_bit0_set", "field40_incremented", "field_ce_incremented",
        "field_c8_cleared", "field36_threshold_branch", "field_c6_updated",
        "returned_to_3754")]

with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "step-counter.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(root / "von/i960/recovered_input_state_step_3540.c"),
                    "-o", str(so)], check=True)
    fn = ctypes.CDLL(str(so)).recovered_input_counter_gate_3658
    fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(CounterGate)]
    for args, expected in (
        ((1, 0x3ff, 0, 0), (1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)),
        ((1, 0x400, 0, 0), (1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)),
        ((0, 0, 1, 1), (0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1)),
        ((0, 2, 1, 1), (0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1)),
        ((0, 2, 1, 2), (0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1)),
    ):
        result = CounterGate()
        fn(*args, ctypes.byref(result))
        actual = tuple(getattr(result, name) for name, _ in CounterGate._fields_)
        assert actual == expected, (args, actual, expected)

print("PASS: 0x3658 input counter gate")


class CounterGate3754(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "status482_bit1_set", "c0_limit_passed", "c0_incremented",
        "c0_cleared", "c0_nonzero_checked", "status480_bit1_checked",
        "status480_bit1_set", "field44_incremented", "field_ce_incremented",
        "field_c8_cleared", "field36_threshold_branch", "field_c6_updated",
        "g7_result", "returned_to_3884")]

with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "step-counter-3754.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(root / "von/i960/recovered_input_state_step_3540.c"),
                    "-o", str(so)], check=True)
    fn = ctypes.CDLL(str(so)).recovered_input_counter_gate_3754
    fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(CounterGate3754)]
    for args, expected in (
        ((2, 0x3ff, 0, 0), (1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)),
        ((2, 0x400, 0, 0), (1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)),
        ((0, 0, 2, 1), (0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1)),
        ((0, 2, 2, 1), (0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1)),
        ((0, 2, 2, 2), (0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1)),
    ):
        result = CounterGate3754()
        fn(*args, ctypes.byref(result))
        actual = tuple(getattr(result, name) for name, _ in CounterGate3754._fields_)
        assert actual == expected, (args, actual, expected)

print("PASS: 0x3754 input counter gate")
