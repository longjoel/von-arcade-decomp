#!/usr/bin/env python3
"""Vectors for the fixed 0x87d38 timing-upload arm."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_secondary_timing_upload_87d38.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [("state_value", ctypes.c_int32),
                ("timing_value", ctypes.c_int32),
                ("timing_aligned", ctypes.c_uint32),
                ("upload_admitted", ctypes.c_uint32),
                ("timing_index", ctypes.c_uint32),
                ("table_offset", ctypes.c_uint32),
                ("indexed_bytes", ctypes.c_uint32),
                ("fixed_bytes", ctypes.c_uint32),
                ("indexed_source_first", ctypes.c_uint32),
                ("indexed_source_second", ctypes.c_uint32),
                ("indexed_destination_first", ctypes.c_uint32),
                ("indexed_destination_second", ctypes.c_uint32),
                ("fixed_source_first", ctypes.c_uint32),
                ("fixed_source_second", ctypes.c_uint32),
                ("fixed_destination_first", ctypes.c_uint32),
                ("fixed_destination_second", ctypes.c_uint32),
                ("upload_call", ctypes.c_uint32),
                ("upload_count", ctypes.c_uint32)]


def main():
    listing = LISTING.read_text()
    for instruction in (r"87d38:.*ld.*0x51d5e4",
                        r"87d40:.*cmpi.*0,g1",
                        r"87d4c:.*addo.*g1,3,g4",
                        r"87d50:.*notand.*g4,3,g4",
                        r"87d54:.*cmpibne.*g1,g4.*0x87de4",
                        r"87d60:.*cmpible.*0,g4.*0x87de4",
                        r"87d78:.*lda.*0x51d5f0",
                        r"87d84:.*call.*0xf5d40",
                        r"87da8:.*lda.*0x5289f0",
                        r"87db0:.*call.*0xf5d40",
                        r"87dbc:.*lda.*0x560df0",
                        r"87dc8:.*call.*0xf5d40",
                        r"87dd4:.*lda.*0x561370",
                        r"87de0:.*call.*0xf5d40"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "upload.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)],
                       check=True)
        function = ctypes.CDLL(str(library)).recovered_stage_secondary_timing_upload_87d38
        function.argtypes = [ctypes.c_int32, ctypes.c_int32]
        function.restype = Result
        skipped = function(0, 0x20)
        assert (skipped.upload_admitted, skipped.upload_count) == (0, 0)
        admitted = function(-1, 0x5a)
        assert (admitted.timing_aligned, admitted.upload_admitted,
                admitted.timing_index, admitted.table_offset) == (0, 1, 0x45, 0x8a00)
        assert (admitted.indexed_source_first, admitted.indexed_source_second) == (0x525ff0, 0x5313f0)
        assert (admitted.fixed_bytes, admitted.upload_count,
                admitted.fixed_source_first, admitted.fixed_source_second,
                admitted.fixed_destination_first, admitted.fixed_destination_second) == (0x580, 4, 0x560df0, 0x561370, 0x565320, 0x5658a0)
    print("recovered 0x87d38 secondary-timing-upload vectors: ok")


if __name__ == "__main__":
    main()
