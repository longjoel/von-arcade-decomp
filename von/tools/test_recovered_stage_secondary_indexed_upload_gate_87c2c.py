#!/usr/bin/env python3
"""Vectors for the fixed 0x87c2c indexed-upload gate."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_secondary_indexed_upload_gate_87c2c.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [("ready_value", ctypes.c_uint32),
                ("state_value", ctypes.c_int32),
                ("timing_value", ctypes.c_int32),
                ("cleanup_call", ctypes.c_uint32),
                ("cleanup_called", ctypes.c_uint32),
                ("upload_gate_admitted", ctypes.c_uint32),
                ("timing_aligned", ctypes.c_uint32),
                ("timing_index", ctypes.c_uint32),
                ("table_offset", ctypes.c_uint32),
                ("first_source", ctypes.c_uint32),
                ("second_source", ctypes.c_uint32),
                ("destination_first", ctypes.c_uint32),
                ("destination_second", ctypes.c_uint32),
                ("upload_bytes", ctypes.c_uint32),
                ("upload_call", ctypes.c_uint32),
                ("common_call_targets", ctypes.c_uint32 * 6)]


def main():
    listing = LISTING.read_text()
    for instruction in (r"87c2c:.*ld.*0x503a7c",
                        r"87c40:.*call.*0xdf070",
                        r"87c4c:.*cmpible.*0.*0x87cbc",
                        r"87c68:.*notand.*g4,3,g4",
                        r"87c84:.*remi.*g3,g4,g4",
                        r"87c94:.*lda.*0x533df0",
                        r"87ca0:.*call.*0xf5d40",
                        r"87ca4:.*lda.*0x5042d0",
                        r"87cb8:.*call.*0xf5d40",
                        r"87cc4:.*call.*0xbece0",
                        r"87cc8:.*call.*0x9b320",
                        r"87ccc:.*call.*0x41f20",
                        r"87cd0:.*call.*0xc5530",
                        r"87cd8:.*call.*0x6fec0",
                        r"87ce4:.*call.*0x71080"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "gate.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)],
                       check=True)
        function = ctypes.CDLL(str(library)).recovered_stage_secondary_indexed_upload_gate_87c2c
        function.argtypes = [ctypes.c_uint32, ctypes.c_int32, ctypes.c_int32]
        function.restype = Result
        clean = function(0, 4, 8)
        assert (clean.cleanup_called, clean.upload_gate_admitted) == (1, 0)
        upload = function(1, -1, 0x5a)
        assert (upload.cleanup_called, upload.upload_gate_admitted,
                upload.timing_aligned, upload.timing_index,
                upload.table_offset) == (0, 1, 0, 0x45, 0x11400)
        assert (upload.first_source, upload.second_source) == (0x5451f0, 0x55b9f0)
        assert list(upload.common_call_targets) == [0xBECE0, 0x9B320, 0x41F20,
                                                    0xC5530, 0x6FEC0, 0x71080]
    print("recovered 0x87c2c secondary-indexed-upload-gate vectors: ok")


if __name__ == "__main__":
    main()
