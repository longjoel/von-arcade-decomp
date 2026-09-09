#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("computed_offset", ctypes.c_uint32),
                ("coordinate0", ctypes.c_uint32),
                ("coordinate1", ctypes.c_uint32),
                ("control_flag", ctypes.c_uint32),
                ("fifo_readback", ctypes.c_uint32),
                ("packet_words", ctypes.c_uint32 * 4),
                ("suffix_word_count", ctypes.c_uint32),
                ("suffix_words", ctypes.c_uint32 * 5),
                ("control_read_address", ctypes.c_uint32),
                ("control_write_address", ctypes.c_uint32),
                ("fallback_asset0", ctypes.c_uint32),
                ("fallback_asset1", ctypes.c_uint32),
                ("fallback_asset2", ctypes.c_uint32),
                ("fallback_status", ctypes.c_uint32),
                ("queued_status", ctypes.c_uint32),
                ("queued_control", ctypes.c_uint32),
                ("queued_descriptor", ctypes.c_uint32),
                ("queued_parameter_address", ctypes.c_uint32),
                ("queued_block_address", ctypes.c_uint32),
                ("fallback_return_target", ctypes.c_uint32),
                ("queued_return_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-object-alt-packet-") as d:
        so = Path(d) / "object-alt-packet.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_object_alternate_packet_e758c.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_object_alternate_packet_e758c
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                       ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        fn.restype = Result
        fallback = fn(0x1000, 0x120, 0x456, 0x789, 0, 0xdeadbeef)
        assert (list(fallback.packet_words), fallback.suffix_word_count,
                list(fallback.suffix_words), fallback.fallback_asset0,
                fallback.fallback_asset1, fallback.fallback_asset2,
                fallback.fallback_status, fallback.fallback_return_target) == \
            ([18, 0x1120, 0x456, 0x789], 5,
             [19, 0x3f800000, 0x3f800000, 0x41200000, 0x13b],
             0x4934b0, 0x493534, 0x900905, 0x101, 0xe7684)
        assert (fallback.control_flag, fallback.fifo_readback) == (0, 0xdeadbeef)
        queued = fn(0x1000, 0x120, 0x456, 0x789, 1, 0x12345678)
        assert (queued.suffix_word_count, queued.queued_status,
                queued.queued_control, queued.queued_descriptor,
                queued.queued_parameter_address, queued.queued_block_address,
                queued.queued_return_target) == \
            (0, 0x101, 0x400020, 0x8fe625, 0x804004, 0x804000, 0xe76cc)
        assert (queued.control_flag, queued.fifo_readback) == (1, 0x12345678)
        print("PASS: 0xe758c alternate object packet")


if __name__ == "__main__":
    main()
