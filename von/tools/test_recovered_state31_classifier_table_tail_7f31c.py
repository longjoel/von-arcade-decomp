#!/usr/bin/env python3
"""Check the classifier table tail at i960 0x7f31c."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state31_classifier_table_tail_7f31c.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "classifier_index", "table_address", "table_value", "related_pointer",
        "result_register", "next_argument", "target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate31-classifier-tail.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state31_classifier_table_tail_7f31c
    function.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Plan)]
    function.restype = None

    for index, value in ((0, 0x11), (3, 0x22), (9, 0x80000000)):
        plan = Plan()
        function(index, value, 0xcafe, ctypes.byref(plan))
        assert (plan.table_address, plan.result_register, plan.next_argument,
                plan.target) == (0x72780 + index * 4, value, 0xcafe, 0x7ecb0)

print("recovered 0x7f31c classifier-tail vectors: ok")
