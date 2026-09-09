#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("saved_base", ctypes.c_uint32),
                ("computed_offset", ctypes.c_uint32),
                ("coordinate0", ctypes.c_uint32),
                ("coordinate1", ctypes.c_uint32),
                ("packet_words", ctypes.c_uint32 * 4),
                ("fifo_address", ctypes.c_uint32),
                ("next_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-object-direct-packet-") as d:
        so = Path(d) / "object-direct-packet.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_object_direct_packet_e7420.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_object_direct_packet_e7420
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                       ctypes.c_uint32, ctypes.c_uint32]
        fn.restype = Result
        out = fn(0x1000, 0x234, 0x456, 0x789)
        assert (out.saved_base, out.computed_offset, out.coordinate0,
                out.coordinate1, list(out.packet_words), out.fifo_address,
                out.next_target) == \
            (0x1000, 0x234, 0x456, 0x789, [18, 0x1234, 0x456, 0x789],
             0x884000, 0xe7454)
        print("PASS: 0xe7420 direct object packet prefix")


if __name__ == "__main__":
    main()
