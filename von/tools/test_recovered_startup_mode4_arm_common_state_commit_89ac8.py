#!/usr/bin/env python3
"""Vectors for the common selector-tail state commit at 0x89ac8."""

import ctypes
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "i960/recovered_startup_mode4_arm_common_state_commit_89ac8.c"
LISTING = ROOT / "build/disasm/vonj-maincpu.lst"


class Result(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "record_30", "record_64", "g14_value", "prior_51d5e0", "state_51c950", "state_51c94c",
        "state_51c954", "state_51c9b4", "state_51d5e0", "state_51c958",
        "state_51c95c", "state_51c960", "state_51c9b4_address", "state_51d5e0_address",
        "return_address")]


def main():
    listing = LISTING.read_text()
    for instruction in (r"89ac8:.*mov.*1,r12", r"89acc:.*st.*r12,0x51c9b4",
                        r"89ad8:.*st.*g14,0x51c9b4", r"89ae0:.*ld.*0x64\(r11\)",
                        r"89ae4:.*cmpibne.*7,g4,0x89af0", r"89ae8:.*st.*g14,0x51d5e0",
                        r"89af0:.*ld.*0x51c950", r"89af8:.*ld.*0x51c94c",
                        r"89b00:.*st.*r13,0x51c958", r"89b08:.*ld.*0x51c954",
                        r"89b10:.*st.*r12,0x51c95c", r"89b18:.*st.*r13,0x51c960",
                        r"89b20:.*ret"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "commit.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-shared", "-fPIC", str(SOURCE), "-o", str(library)], check=True)
        function = ctypes.CDLL(str(library)).recovered_startup_mode4_arm_common_state_commit_89ac8
        function.argtypes = [ctypes.c_uint32] * 7
        function.restype = Result

        zero_record = function(0, 6, 0xdeadbeef, 0x999, 0x111, 0x222, 0x333)
        assert (zero_record.state_51c9b4, zero_record.state_51d5e0,
                zero_record.state_51c958, zero_record.state_51c95c,
                zero_record.state_51c960) == (1, 0x999, 0x111, 0x222, 0x333)

        flagged = function(5, 7, 0xdeadbeef, 0x999, 0x444, 0x555, 0x666)
        assert (flagged.state_51c9b4, flagged.state_51d5e0,
                flagged.state_51c958, flagged.state_51c95c,
                flagged.state_51c960, flagged.state_51d5e0_address,
                flagged.return_address) == (0xdeadbeef, 0xdeadbeef, 0x444,
                                              0x555, 0x666, 0x51d5e0, 0x89b20)
    print("recovered 0x89ac8 common-state-commit vectors: ok")


if __name__ == "__main__":
    main()
