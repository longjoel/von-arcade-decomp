#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("object_tag_byte", ctypes.c_uint32),
                ("caller_tag_byte", ctypes.c_uint32),
                ("tags_match", ctypes.c_uint32),
                ("special_caller_tag", ctypes.c_uint32),
                ("special_match", ctypes.c_uint32),
                ("helper_target", ctypes.c_uint32),
                ("route", ctypes.c_uint32),
                ("accepted_target", ctypes.c_uint32),
                ("rejected_target", ctypes.c_uint32),
                ("emitter_dispatch_target", ctypes.c_uint32),
                ("direct_packet_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-object-fallback-admission-") as d:
        so = Path(d) / "object-fallback-admission.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_object_fallback_admission_e76d0.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_object_fallback_admission_e76d0
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        fn.restype = Result
        matching = fn(0x104, 4, 0)
        assert (matching.tags_match, matching.special_match, matching.route) == (1, 0, 2)
        special = fn(0x103, 62, 1)
        assert (special.tags_match, special.special_match, special.route) == (0, 1, 3)
        rejected = fn(0x103, 4, 0)
        assert (rejected.tags_match, rejected.special_match, rejected.route) == (0, 0, 0)
        assert (rejected.helper_target, rejected.accepted_target,
                rejected.rejected_target, rejected.emitter_dispatch_target,
                rejected.direct_packet_target) == \
            (0xf50c8, 0xe76fc, 0xe7850, 0xe7340, 0xe7874)
        print("PASS: 0xe76d0 fallback object admission")


if __name__ == "__main__":
    main()
