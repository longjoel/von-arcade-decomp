#!/usr/bin/env python3
"""Test the 0x784c8 selector-table dispatch boundary."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_selector_dispatch.c"


class SelectorPlan(ctypes.Structure):
    _fields_ = [
        ("target", ctypes.c_uint32),
        ("writes_flag", ctypes.c_uint32),
        ("flag_value", ctypes.c_uint32),
    ]


class ActionState(ctypes.Structure):
    _fields_ = [
        ("transition", ctypes.c_uint32),
        ("action", ctypes.c_uint32),
    ]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-transition-selector-") as directory:
        library = Path(directory) / "transition-selector.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        target = recovered.recovered_transition_selector_target
        target.argtypes = [ctypes.c_uint32]
        target.restype = ctypes.c_uint32

        expected = [
            0x00078508, 0x00078524, 0x00078540, 0x00078560, 0x0007857C,
            0x0007859C, 0x000785BC, 0x000785D8, 0x000785F8, 0x00078618,
        ]
        for selector, address in enumerate(expected):
            if target(selector) != address:
                raise SystemExit(f"selector {selector} target mismatch")
        for selector in (10, 0xFFFFFFFF):
            if target(selector) != 0:
                raise SystemExit(f"out-of-range selector 0x{selector:x} did not return")

        flag = recovered.recovered_transition_selector_flag
        flag.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        flag.restype = ctypes.c_uint32
        for selector in range(10):
            for mode_bits in range(8):
                expected_flag = (
                    (mode_bits & 0x2) != 0 if selector in (0, 6)
                    else (mode_bits & 0x4) != 0 if selector in (1, 3)
                    else (mode_bits & 0x6) != 0
                )
                if flag(selector, mode_bits) != int(expected_flag):
                    raise SystemExit(f"selector {selector} flag mismatch for mode 0x{mode_bits:x}")
        if flag(10, 0xFFFFFFFF) != 0:
            raise SystemExit("out-of-range selector wrote flag")

        plan = recovered.recovered_transition_selector_plan
        plan.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(SelectorPlan)]
        plan.restype = None
        combined = SelectorPlan()
        plan(0, 0x2, ctypes.byref(combined))
        if (combined.target, combined.writes_flag, combined.flag_value) != (0x00078508, 1, 1):
            raise SystemExit("combined selector plan mismatch")
        plan(3, 0x2, ctypes.byref(combined))
        if (combined.target, combined.writes_flag, combined.flag_value) != (0x00078560, 0, 0):
            raise SystemExit("combined false selector plan mismatch")
        plan(10, 0xFFFFFFFF, ctypes.byref(combined))
        if (combined.target, combined.writes_flag, combined.flag_value) != (0, 0, 0):
            raise SystemExit("combined out-of-range selector plan mismatch")

        action5 = recovered.recovered_transition_action5_table_value
        action5.argtypes = [ctypes.c_uint32]
        action5.restype = ctypes.c_uint32
        action10 = recovered.recovered_transition_action10_table_value
        action10.argtypes = [ctypes.c_uint32]
        action10.restype = ctypes.c_uint32
        if [action5(i) for i in range(10)] != [8, 12, 12, 12, 12, 13, 13, 13, 19, 8]:
            raise SystemExit("action-5 ROM table mismatch")
        if [action10(i) for i in range(10)] != [9, 16, 12, 12, 12, 13, 13, 13, 17, 9]:
            raise SystemExit("action-10 ROM table mismatch")
        if action5(10) != 0 or action10(10) != 0:
            raise SystemExit("action table bounds mismatch")

        apply5 = recovered.recovered_transition_apply_action5
        apply5.argtypes = [ctypes.c_uint32, ctypes.POINTER(ActionState)]
        apply5.restype = ctypes.c_uint32
        apply10 = recovered.recovered_transition_apply_action10
        apply10.argtypes = [ctypes.c_uint32, ctypes.POINTER(ActionState)]
        apply10.restype = ctypes.c_uint32
        action_state = ActionState(0, 0)
        if apply5(8, ctypes.byref(action_state)) != 1 or (action_state.transition, action_state.action) != (19, 5):
            raise SystemExit("action-5 state application mismatch")
        if apply10(8, ctypes.byref(action_state)) != 1 or (action_state.transition, action_state.action) != (17, 10):
            raise SystemExit("action-10 state application mismatch")
        if apply5(10, ctypes.byref(action_state)) != 0 or apply10(10, ctypes.byref(action_state)) != 0:
            raise SystemExit("action application bounds mismatch")

    print("PASS: 0x784c8 selector dispatch, handler predicates, and unsigned bounds")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
