#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("computed_offset", ctypes.c_uint32),
                ("control_word", ctypes.c_uint32),
                ("control_flag", ctypes.c_uint32),
                ("fifo_readback", ctypes.c_uint32),
                ("common_fifo_words", ctypes.c_uint32 * 2),
                ("fifo_address", ctypes.c_uint32),
                ("control_read_address", ctypes.c_uint32),
                ("control_write_address", ctypes.c_uint32),
                ("control_write_value", ctypes.c_uint32),
                ("route", ctypes.c_uint32),
                ("fallback_asset0", ctypes.c_uint32),
                ("fallback_asset1", ctypes.c_uint32),
                ("fallback_asset2", ctypes.c_uint32),
                ("fallback_status", ctypes.c_uint32),
                ("fallback_status_address", ctypes.c_uint32),
                ("queued_status", ctypes.c_uint32),
                ("queued_control", ctypes.c_uint32),
                ("queued_parameter_address", ctypes.c_uint32),
                ("queued_parameter", ctypes.c_uint32),
                ("queued_block_address", ctypes.c_uint32),
                ("return_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-object-packet-response-") as d:
        so = Path(d) / "object-packet-response.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_object_packet_response_e7490.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_object_packet_response_e7490
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                       ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        fn.restype = Result
        fallback = fn(0x120, 0x4000, 0, 0xdeadbeef, 0)
        assert (fallback.control_flag, fallback.fifo_readback) == (0, 0xdeadbeef)
        assert (list(fallback.common_fifo_words), fallback.control_write_value,
                fallback.route, fallback.fallback_asset0, fallback.fallback_asset1,
                fallback.fallback_asset2, fallback.fallback_status,
                fallback.fallback_status_address, fallback.return_target) == \
            ([0x13b, 0x4000], 0x4034, 0, 0x49317c, 0x4931ac, 0x900514,
             0x101, 0x800010, 0xe7514)
        queued = fn(0x120, 0x4000, 1, 0xcafebabe, 0x12345678)
        assert (queued.control_flag, queued.fifo_readback) == (1, 0xcafebabe)
        assert (queued.route, queued.queued_status, queued.queued_control,
                queued.queued_parameter_address, queued.queued_parameter,
                queued.queued_block_address, queued.return_target) == \
            (1, 0x101, 0x400020, 0x804004, 0x12345678, 0x804000, 0xe755c)
        print("PASS: 0xe7490 object packet response split")


if __name__ == "__main__":
    main()
