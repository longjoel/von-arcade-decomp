#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("input_phase", ctypes.c_int32),
                ("clamped_phase", ctypes.c_int32),
                ("stored_phase", ctypes.c_int32),
                ("phase_address", ctypes.c_uint32),
                ("lower_bound", ctypes.c_uint32),
                ("upper_bound", ctypes.c_uint32),
                ("quantization_shift", ctypes.c_uint32),
                ("quantization_mask", ctypes.c_uint32),
                ("fifo_address", ctypes.c_uint32),
                ("first_command", ctypes.c_uint32),
                ("second_command", ctypes.c_uint32),
                ("third_command", ctypes.c_uint32),
                ("final_command", ctypes.c_uint32),
                ("next_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-geometry-phase-") as d:
        so = Path(d) / "geometry-phase.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_status_emit_phase_prefix_e6d80.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_status_emit_phase_prefix_e6d80
        fn.argtypes = [ctypes.c_int32]
        fn.restype = Result
        for phase, clamped in ((-1, 0), (0, 0), (17, 17), (40, 40), (41, 40)):
            out = fn(phase)
            assert (out.clamped_phase, out.stored_phase) == (clamped, clamped - 1)
        out = fn(17)
        assert (out.phase_address, out.lower_bound, out.upper_bound,
                out.quantization_shift, out.quantization_mask, out.fifo_address,
                out.first_command, out.second_command, out.third_command,
                out.final_command, out.next_target) == \
            (0x5783d8, 0, 40, 10, 0xfc00, 0x884000, 29, 29, 30, 18, 0xe6ee8)
        print("PASS: 0xe6d80 geometry emitter phase prefix")


if __name__ == "__main__":
    main()
