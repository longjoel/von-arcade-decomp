#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]

class Plan(ctypes.Structure):
    _fields_ = [
        ("plus_6000", ctypes.c_uint32),
        ("minus_6000", ctypes.c_uint32),
        ("center", ctypes.c_uint32),
    ]

with tempfile.TemporaryDirectory() as d:
    so = pathlib.Path(d) / "fifo_plan.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2", "-o", str(so),
        str(ROOT / "von/i960/recovered_geometry_fifo_argument_plan_76240.c"),
    ], check=True)
    fn = ctypes.CDLL(str(so)).recovered_geometry_fifo_argument_plan_76240
    fn.argtypes = [ctypes.c_uint16]
    fn.restype = Plan
    for raw, expected in (
        (0x0000, (0x6000, 0xa000, 0x0000)),
        (0x8000, (0xe000, 0x2000, 0x8000)),
        (0xe000, (0x4000, 0x8000, 0xe000)),
        (0xffff, (0x5fff, 0x9fff, 0xffff)),
    ):
        got = fn(raw)
        assert (got.plus_6000, got.minus_6000, got.center) == expected, (raw, got, expected)

print("PASS: original 0x76240 FIFO argument arithmetic vectors")
