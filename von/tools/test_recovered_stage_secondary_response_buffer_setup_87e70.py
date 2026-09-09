#!/usr/bin/env python3
"""Vectors for the fixed 0x87e70 response-buffer/setup block."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_secondary_response_buffer_setup_87e70.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [("state_value", ctypes.c_int32),
                ("upload_admitted", ctypes.c_uint32),
                ("first_source", ctypes.c_uint32),
                ("second_source", ctypes.c_uint32),
                ("first_destination", ctypes.c_uint32),
                ("second_destination", ctypes.c_uint32),
                ("upload_bytes", ctypes.c_uint32),
                ("upload_call", ctypes.c_uint32),
                ("callback_first_address", ctypes.c_uint32),
                ("callback_second_address", ctypes.c_uint32),
                ("callback_value", ctypes.c_uint32),
                ("callback_store_count", ctypes.c_uint32),
                ("phase_address", ctypes.c_uint32),
                ("phase_value", ctypes.c_uint32),
                ("formatter_target", ctypes.c_uint32),
                ("formatter_argument_0", ctypes.c_uint32),
                ("formatter_argument_1", ctypes.c_uint32),
                ("renderer_source", ctypes.c_uint32),
                ("renderer_target", ctypes.c_uint32)]


def main():
    listing = LISTING.read_text()
    for instruction in (r"87e70:.*ld.*0x51c988",
                        r"87e78:.*cmpible.*0.*0x87ebc",
                        r"87e84:.*lda.*0x51c9e0",
                        r"87e90:.*call.*0xf5d40",
                        r"87e94:.*lda.*0x5040d0",
                        r"87e9c:.*lda.*0x51cfe0",
                        r"87eac:.*st.*0x503c4a",
                        r"87eb4:.*st.*0x50424a",
                        r"87ec4:.*st.*0x503a00",
                        r"87ed0:.*bal.*0x1cac8",
                        r"87edc:.*call.*0x1da90"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "setup.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)],
                       check=True)
        function = ctypes.CDLL(str(library)).recovered_stage_secondary_response_buffer_setup_87e70
        function.argtypes = [ctypes.c_int32, ctypes.c_uint32]
        function.restype = Result
        negative = function(-1, 0x12345678)
        assert (negative.upload_admitted, negative.first_source,
                negative.second_source, negative.upload_bytes) == (1, 0x51C9E0, 0x51CFE0, 0x600)
        assert (negative.callback_value, negative.callback_store_count,
                negative.phase_value) == (0x12345678, 2, 12)
        assert (negative.formatter_target, negative.formatter_argument_0,
                negative.formatter_argument_1, negative.renderer_source,
                negative.renderer_target) == (0x1CAC8, 21, 14, 0x87AA0, 0x1DA90)
        positive = function(0, 0)
        assert positive.upload_admitted == 0 and positive.callback_store_count == 2
    print("recovered 0x87e70 secondary-response-buffer-setup vectors: ok")


if __name__ == "__main__":
    main()
