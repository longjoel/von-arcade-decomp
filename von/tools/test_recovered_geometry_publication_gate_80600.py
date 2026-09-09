#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_publication_gate_80600.c"

class Plan(ctypes.Structure):
    _fields_ = [(name, ctype) for name, ctype in (
        ("global_counter", ctypes.c_uint32), ("counter_threshold", ctypes.c_uint32),
        ("comparison_value", ctypes.c_int32), ("first_threshold", ctypes.c_int32),
        ("mode_word", ctypes.c_uint32), ("second_threshold", ctypes.c_int32),
        ("third_threshold", ctypes.c_int32),
        ("counter_gate_passed", ctypes.c_uint32),
        ("first_comparison_passed", ctypes.c_uint32),
        ("mode4_comparison_passed", ctypes.c_uint32),
        ("mode5_comparison_passed", ctypes.c_uint32),
        ("publication_gate_passed", ctypes.c_uint32), ("target", ctypes.c_uint32),
    )]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "publication-gate.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_geometry_publication_gate_80600
    build.argtypes = [
        ctypes.c_uint32, ctypes.c_int32, ctypes.c_int32, ctypes.c_uint32,
        ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(Plan)]

    plan = Plan()
    build(0x5dd, 10, 11, 0, 20, 30, ctypes.byref(plan))
    assert plan.counter_gate_passed == 1
    assert plan.first_comparison_passed == 1
    assert plan.publication_gate_passed == 1
    assert plan.target == 0x80650

    build(0x5dd, 20, 10, 4, 21, 30, ctypes.byref(plan))
    assert plan.mode4_comparison_passed == 1
    assert plan.target == 0x80650

    build(0x5dd, 30, 10, 5, 20, 31, ctypes.byref(plan))
    assert plan.mode5_comparison_passed == 1
    assert plan.target == 0x80650

    build(0x5dc, 0, 1, 0, 1, 1, ctypes.byref(plan))
    assert plan.counter_gate_passed == 0
    assert plan.target == 0x806F4

    build(0x5dd, 10, 10, 3, 20, 30, ctypes.byref(plan))
    assert plan.publication_gate_passed == 0
    assert plan.target == 0x806F4

print("recovered 0x80600 publication-gate vectors: ok")
