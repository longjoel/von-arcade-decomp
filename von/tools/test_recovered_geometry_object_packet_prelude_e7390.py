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
                ("queue_flag", ctypes.c_uint32),
                ("route", ctypes.c_uint32),
                ("mismatch_target", ctypes.c_uint32),
                ("emitter_dispatch_target", ctypes.c_uint32),
                ("direct_packet_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-object-packet-prelude-") as d:
        so = Path(d) / "object-packet-prelude.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_object_packet_prelude_e7390.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_object_packet_prelude_e7390
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        fn.restype = Result
        mismatch = fn(0x102, 0x03, 0)
        assert (mismatch.object_tag_byte, mismatch.caller_tag_byte,
                mismatch.tags_match, mismatch.route) == (2, 3, 0, 0)
        emitter = fn(0x103, 0x03, 0)
        assert (emitter.tags_match, emitter.route) == (1, 1)
        direct = fn(0x103, 0x03, 7)
        assert (direct.tags_match, direct.route) == (1, 2)
        assert (direct.mismatch_target, direct.emitter_dispatch_target,
                direct.direct_packet_target) == (0xe7560, 0xe7340, 0xe7420)
        print("PASS: 0xe7390 object packet admission prelude")


if __name__ == "__main__":
    main()
