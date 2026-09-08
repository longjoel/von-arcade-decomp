#!/usr/bin/env python3
"""Validate the callback-returning 0x7a318 transition setup plan."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_setup_7a318.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "route", "writes_504d84", "value_504d84",
        "writes_504d98", "value_504d98",
        "writes_504db8", "value_504db8",
        "writes_504d94", "value_504d94")]


with tempfile.TemporaryDirectory(prefix="von-transition-setup-") as directory:
    library = pathlib.Path(directory) / "transition-setup.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_setup_7a318
    function.argtypes = [ctypes.c_uint32] * 5 + [ctypes.POINTER(Plan)]
    function.restype = None

    def plan(state, gate=0, cursor=100, reference_a=100, reference_b=70):
        result = Plan()
        function(state, gate, cursor, reference_a, reference_b,
                 ctypes.byref(result))
        return result

    # The five exact states share the cursor publication path.
    for state in (1, 2, 4, 5, 7):
        result = plan(state)
        assert result.route == 0
        assert result.writes_504db8 == 1
        assert result.value_504db8 == 122  # cursor + 22 wins here
        assert result.writes_504d94 == 0

    # When reference_a+31 is below cursor+22, the g29+31 alternative wins.
    result = plan(1, cursor=100, reference_a=50, reference_b=70)
    assert result.value_504db8 == 101

    # State-minus-one <= 3 takes the 12 arm; larger unsigned values take 13.
    # State zero wraps to 0xffffffff before the unsigned comparison.
    for state in (3,):
        result = plan(state)
        assert (result.route, result.writes_504d94, result.value_504d94) == (1, 1, 12)
    for state in (0, 6, 8, 9, 10, 0xffffffff):
        result = plan(state)
        assert (result.route, result.writes_504d94, result.value_504d94) == (2, 1, 13)

    # The control gate independently publishes 1 to both transition globals.
    result = plan(4, gate=1)
    assert (result.writes_504d84, result.value_504d84,
            result.writes_504d98, result.value_504d98) == (1, 1, 1, 1)
    assert (result.writes_504db8, result.value_504db8) == (1, 122)
    result = plan(6, gate=1)
    assert (result.writes_504d84, result.value_504d84,
            result.writes_504d98, result.value_504d98) == (1, 1, 1, 1)
    assert (result.writes_504db8, result.value_504db8,
            result.writes_504d94) == (1, 10, 0)

print("PASS: 0x7a318 transition-setup vectors")
