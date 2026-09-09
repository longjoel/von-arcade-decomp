#!/usr/bin/env python3
"""Vectors for the shared mode-4 dispatch gate at 0x89b30."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_common_dispatch_89b30.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "counter_51c984", "g14_value", "current_record_8", "current_record_10",
        "linked_record_8", "linked_record_10", "fifo_response", "selector_51c99c",
        "packet_10_0", "packet_10_1", "packet_10_2", "state_51c940", "fifo_address",
        "command", "target")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"89b30:.*addo.*16,sp,sp", r"89b34:.*ld.*0x51c984",
                        r"89b3c:.*addo.*31,28,r12", r"89b40:.*ld.*0x74\(g0\)",
                        r"89b44:.*cmpi.*g4,r12", r"89b50:.*st.*g14,0x51c99c",
                        r"89b5c:.*lda.*0x77", r"89b60:.*cmpibg.*g4,r13,0x89b74",
                        r"89b68:.*st.*r12,0x51c99c", r"89b74:.*lda.*0x95",
                        r"89b78:.*cmpibg.*g4,r13,0x89b8c", r"89b80:.*st.*r12,0x51c99c",
                        r"89b90:.*st.*r13,0x51c99c", r"89b98:.*ld.*0x10\(g0\)",
                        r"89b9c:.*ld.*0x10\(r10\)", r"89ba0:.*ld.*0x8\(r10\)",
                        r"89ba4:.*ld.*0x8\(g0\)", r"89ba8:.*subr.*g7,g5,g5",
                        r"89bac:.*subr.*g6,g4,g4", r"89bb0:.*mov.*10,r12",
                        r"89bbc:.*st.*g5,0x884000", r"89bc4:.*st.*g4,0x884000",
                        r"89bd4:.*ld.*0x884000", r"89be0:.*stos.*g2,0x51c940",
                        r"89be8:.*be.*0x89e44", r"89bf8:.*cmpibe.*2,g4,0x8a178",
                        r"89bfc:.*cmpibe.*3,g4,0x8a4bc", r"89c04:.*ld.*0x51c984"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "dispatch.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_common_dispatch_89b30
        function.argtypes = [ctypes.c_uint32] * 7
        function.restype = Result
        low = function(59, 5, 0x100, 0x200, 0x300, 0x400, 0x55)
        assert (low.selector_51c99c, low.packet_10_0, low.packet_10_1,
                low.packet_10_2, low.state_51c940, low.target) == (5, 10, 0xfffffe00,
                                                                     0x200, 0x55, 0)
        mid = function(0x78, 5, 0x100, 0x200, 0x300, 0x400, 0x66)
        assert (mid.selector_51c99c, mid.target) == (2, 0x8a178)
        high = function(0x96, 5, 0x100, 0x200, 0x300, 0x400, 0x77)
        assert (high.selector_51c99c, high.target, high.fifo_address,
                high.command) == (3, 0x8a4bc, 0x884000, 10)
    print("recovered 0x89b30 common-dispatch vectors: ok")


if __name__ == "__main__":
    main()
