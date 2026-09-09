#!/usr/bin/env python3
"""Vectors for post-selector packet dispatch at 0x8a890."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_8a890_post_dispatch.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "selector_51c99c", "current_record_8", "current_record_10", "linked_record_8",
        "linked_record_10", "fifo_response", "packet_10_0", "packet_10_1",
        "packet_10_2", "state_51c940", "fifo_address", "command", "target")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"8a890:.*addo.*16,sp,sp", r"8a894:.*ld.*0x51c984",
                        r"8a8a0:.*ld.*0x74\(g0\)", r"8a8ac:.*bg.*0x8a8bc",
                        r"8a8b0:.*st.*g14,0x51c99c", r"8a8bc:.*lda.*0x77",
                        r"8a8c0:.*cmpibg.*g4,r12,0x8a8d4",
                        r"8a8d4:.*lda.*0x95", r"8a8d8:.*cmpibg.*g4,r12,0x8a8ec",
                        r"8a8ec:.*mov.*3,r12", r"8a8f8:.*ld.*0x10\(g0\)",
                        r"8a900:.*ld.*0x8\(r10\)", r"8a910:.*mov.*10,r13",
                        r"8a91c:.*st.*g5,0x884000", r"8a924:.*st.*g4,0x884000",
                        r"8a92c:.*ld.*0x51c99c", r"8a934:.*ld.*0x884000,g2",
                        r"8a940:.*stos.*g2,0x51c940", r"8a948:.*be.*0x8aba4",
                        r"8a958:.*cmpibe.*2,g4,0x8aed8", r"8a95c:.*cmpibe.*3,g4,0x8b21c"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "dispatch.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_8a890_post_dispatch
        function.argtypes = [ctypes.c_uint32] * 6
        function.restype = Result
        result = function(2, 0x100, 0x200, 0x300, 0x400, 0x55)
        assert (result.packet_10_0, result.packet_10_1, result.packet_10_2,
                result.state_51c940, result.target) == (10, 0xfffffe00, 0x200,
                                                        0x55, 0x8aed8)
        for selector, target in ((0, 0x8a964), (1, 0x8aba4), (3, 0x8b21c),
                                 (4, 0)):
            assert function(selector, 0, 0, 0, 0, 0).target == target
    print("recovered 0x8a890 post-dispatch vectors: ok")


if __name__ == "__main__":
    main()
