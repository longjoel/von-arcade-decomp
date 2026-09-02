#!/usr/bin/env python3
"""Test the unified context-based object-state dispatcher."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCES = [
    ROOT / "von/i960/recovered_object_state_dispatch.c",
    ROOT / "von/i960/recovered_object_state_zero.c",
    ROOT / "von/i960/recovered_object_state_one.c",
    ROOT / "von/i960/recovered_object_state_two.c",
    ROOT / "von/i960/recovered_object_state_three.c",
    ROOT / "von/i960/recovered_object_state_four.c",
    ROOT / "von/i960/recovered_object_state_five.c",
    ROOT / "von/i960/recovered_object_state_six.c",
    ROOT / "von/i960/recovered_object_state_seven.c",
    ROOT / "von/i960/recovered_object_state_terminal.c",
]


class Context(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "state", "timer_bits", "mode_bits", "role_d94", "object_d68",
        "related_state", "related_tag", "global_state", "global_substate",
        "caller_state",
    )]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-object-state-dispatch-") as directory:
        library = Path(directory) / "object-state-dispatch.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", *SOURCES, "-o", library],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        dispatch = recovered.recovered_object_state_dispatch
        dispatch.argtypes = [ctypes.POINTER(Context), ctypes.POINTER(ctypes.c_uint32)]
        dispatch.restype = ctypes.c_uint32

        for state in range(12):
            context = Context(
                state=state,
                timer_bits=0,
                mode_bits=0,
                role_d94=5,
                object_d68=0,
                related_state=0,
                related_tag=0,
                global_state=0,
                global_substate=0,
                caller_state=0,
            )
            transition = ctypes.c_uint32(0xA5A5A5A5)
            changed = bool(dispatch(ctypes.byref(context), ctypes.byref(transition)))
            if state in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9):
                assert changed
            else:
                assert not changed
                assert transition.value == 0xA5A5A5A5

        # Verify context field routing through representative non-default arms.
        context = Context(1, 0, 2, 0, 7, 0, 0, 0, 0, 0)
        transition = ctypes.c_uint32(0xA5A5A5A5)
        assert dispatch(ctypes.byref(context), ctypes.byref(transition)) == 1
        assert transition.value == 8
        context = Context(7, 0, 4, 0, 0, 4, 0, 4, 0, 2)
        transition.value = 0xA5A5A5A5
        assert dispatch(ctypes.byref(context), ctypes.byref(transition)) == 1
        assert transition.value == 9

    print("recovered object-state unified dispatcher vectors: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
