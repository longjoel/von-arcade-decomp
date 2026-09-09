#!/usr/bin/env python3
"""Vectors for the bounded 0x87ac0 secondary probe/retry controller."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_secondary_probe_loop_87ac0.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [("phase", ctypes.c_uint32),
                ("initial_probe_result", ctypes.c_uint32),
                ("first_callback_result", ctypes.c_uint32),
                ("retry_callback_results", ctypes.c_uint32 * 5),
                ("retry_count", ctypes.c_uint32),
                ("helper_8d108_called", ctypes.c_uint32),
                ("helper_8d108_target", ctypes.c_uint32),
                ("tail_target", ctypes.c_uint32),
                ("continuation", ctypes.c_uint32)]


def main():
    listing = LISTING.read_text()
    for instruction in (r"87ac0:.*ldob.*0x1a14002",
                        r"87ad0:.*cmpibne.*20.*0x87b2c",
                        r"87ad4:.*bal.*0x8d0d8",
                        r"87adc:.*bal.*0x87a18",
                        r"87ae4:.*bal.*0x8d108",
                        r"87af0:.*call.*0x18ab0",
                        r"87b0c:.*cmpibge.*4.*0x87af4",
                        r"87b10:.*call.*0x294b0"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "probe.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)],
                       check=True)
        function = ctypes.CDLL(str(library)).recovered_stage_secondary_probe_loop_87ac0
        function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                             ctypes.POINTER(ctypes.c_uint32)]
        function.restype = Result

        zeros = (ctypes.c_uint32 * 5)(0, 0, 0, 0, 0)
        direct = function(19, 0, 0, zeros)
        assert direct.tail_target == 0
        assert direct.continuation == 0x87B2C

        first = function(19, 1, 0, zeros)
        assert (first.helper_8d108_called, first.tail_target,
                first.retry_count) == (1, 0x87B10, 0)

        retry = (ctypes.c_uint32 * 5)(0, 0, 1, 0, 0)
        recovered = function(19, 1, 1, retry)
        assert (recovered.helper_8d108_called, recovered.tail_target,
                recovered.retry_count) == (1, 0x87B10, 3)

        exhausted = function(19, 1, 1, zeros)
        assert (exhausted.helper_8d108_called, exhausted.tail_target,
                exhausted.retry_count) == (0, 0x87B10, 5)
    print("recovered 0x87ac0 secondary-probe-loop vectors: ok")


if __name__ == "__main__":
    main()
