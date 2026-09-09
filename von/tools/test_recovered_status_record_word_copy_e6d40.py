#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Plan(ctypes.Structure):
    _fields_ = [("halfword_count", ctypes.c_uint32),
                ("source_stride", ctypes.c_uint32),
                ("destination_stride", ctypes.c_uint32),
                ("source_load_width", ctypes.c_uint32),
                ("destination_store_width", ctypes.c_uint32),
                ("indirect_target", ctypes.c_uint32),
                ("return_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-status-copy-") as d:
        so = Path(d) / "status-copy.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_status_record_word_copy_e6d40.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        plan = lib.recovered_status_record_word_copy_plan_e6d40
        plan.restype = Plan
        out = plan()
        assert (out.halfword_count, out.source_stride, out.destination_stride,
                out.source_load_width, out.destination_store_width,
                out.indirect_target, out.return_target) == \
            (0x200, 2, 2, 2, 2, 0xe6d78, 0xe6d78)

        copy = lib.recovered_status_record_word_copy_e6d40
        copy.argtypes = [ctypes.POINTER(ctypes.c_uint16),
                         ctypes.POINTER(ctypes.c_int16)]
        source = (ctypes.c_int16 * 0x200)(*[(i * 37) % 32767 for i in range(0x200)])
        destination = (ctypes.c_uint16 * 0x200)()
        copy(destination, source)
        assert list(destination) == [value & 0xffff for value in source]
        print("PASS: 0xe6d40 0x200-halfword status copy")


if __name__ == "__main__":
    main()
