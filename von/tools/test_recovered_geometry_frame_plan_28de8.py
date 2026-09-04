#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class Plan(ctypes.Structure):
    _fields_ = [("read_start", ctypes.c_uint32),
                ("expected_status_bit", ctypes.c_uint32),
                ("completed", ctypes.c_uint32),
                ("next_phase", ctypes.c_uint32),
                ("write_start", ctypes.c_uint32)]

def main():
    with tempfile.TemporaryDirectory() as d:
        so = Path(d) / "frame.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        str(ROOT / "von/i960/recovered_geometry_frame_plan_28de8.c"), "-o", so], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_frame_plan_28de8
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                       ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(Plan)]
        for phase in (0, 1, 2, 0xffffffff):
            for before in (0, 4, 0x104):
                spins = ctypes.c_uint32(3); plan = Plan()
                fn(phase, before, before ^ 4, ctypes.byref(spins), ctypes.byref(plan))
                assert plan.completed == 1
                assert plan.expected_status_bit == before & 4
                assert plan.next_phase == ((phase & 1) ^ 1)
                assert plan.read_start == (0x10000 if phase & 1 else 0)
                assert plan.write_start == (0x10000 if not phase & 1 else 0)
                spins = ctypes.c_uint32(3)
                fn(phase, before, before, ctypes.byref(spins), ctypes.byref(plan))
                assert plan.completed == 0 and spins.value == 0x1000

if __name__ == "__main__":
    main()
