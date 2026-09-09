#!/usr/bin/env python3
"""Vectors for the fixed 0x87e10 response publication gate."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_stage_secondary_response_publication_gate_87e10.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [("state_value", ctypes.c_uint32),
                ("frame_index_r29", ctypes.c_uint32),
                ("state_threshold", ctypes.c_uint32),
                ("flag_word_5024a4", ctypes.c_uint32),
                ("ready_value", ctypes.c_uint32),
                ("exception_word_5024f4", ctypes.c_uint32),
                ("response_value_51c9d0", ctypes.c_uint32),
                ("seed_value", ctypes.c_uint32),
                ("publication_reached", ctypes.c_uint32),
                ("response_one_store", ctypes.c_uint32),
                ("response_zero_store", ctypes.c_uint32),
                ("response_one_address", ctypes.c_uint32),
                ("response_zero_address", ctypes.c_uint32),
                ("publication_target", ctypes.c_uint32),
                ("return_target", ctypes.c_uint32)]


def main():
    listing = LISTING.read_text()
    for instruction in (r"87e10:.*ld.*0x51c988",
                        r"87e18:.*addo.*31,29,g3",
                        r"87e1c:.*cmpibg.*0x87e50",
                        r"87e28:.*bbs.*4.*0x87e50",
                        r"87e34:.*cmpibe.*0.*0x87f50",
                        r"87e44:.*cmpibe.*g4,g3.*0x87e50",
                        r"87e4c:.*cmpibne.*g4,g3.*0x87f50",
                        r"87e50:.*ld.*0x51c9d0",
                        r"87e58:.*cmpibne.*1,g4.*0x87e64",
                        r"87e5c:.*st.*0x503ca2",
                        r"87e64:.*cmpibne.*0,g4.*0x87e70",
                        r"87e68:.*st.*0x5042a2"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "gate.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)],
                       check=True)
        function = ctypes.CDLL(str(library)).recovered_stage_secondary_response_publication_gate_87e10
        function.argtypes = [ctypes.c_uint32] * 7
        function.restype = Result
        response_one = function(34, 2, 0, 0, 0, 1, 0x55)
        assert (response_one.state_threshold, response_one.publication_reached,
                response_one.response_one_store, response_one.response_zero_store) == (33, 1, 1, 0)
        response_zero = function(34, 2, 0, 0, 0, 0, 0x55)
        assert (response_zero.response_one_store, response_zero.response_zero_store) == (0, 1)
        blocked = function(20, 2, 0, 0, 0x61, 1, 0x55)
        assert blocked.publication_reached == 0 and blocked.response_one_store == 0
        ready = function(20, 2, 0, 1, 0x61, 1, 0x55)
        assert ready.publication_reached == 1 and ready.response_one_store == 1
    print("recovered 0x87e10 secondary-response-publication-gate vectors: ok")


if __name__ == "__main__":
    main()
