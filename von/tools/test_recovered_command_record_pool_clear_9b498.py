#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Pool(ctypes.Structure):
    _fields_ = [("record_bytes", (ctypes.c_uint8 * 16) * 16),
                ("cursor", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-command-record-clear-") as d:
        so = Path(d) / "command-record-clear.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        str(ROOT / "von/i960/recovered_command_record_pool_clear_9b498.c"),
                        "-o", str(so)], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_command_record_pool_clear_9b498
        fn.argtypes = [ctypes.POINTER(Pool)]
        state = Pool()
        ctypes.memset(ctypes.byref(state), 0xa5, ctypes.sizeof(state))
        state.cursor = 0xdeadbeef
        fn(ctypes.byref(state))
        assert all(state.record_bytes[i][0] == 0 for i in range(16))
        assert all(state.record_bytes[i][j] == 0xa5
                   for i in range(16) for j in range(1, 16))
        assert state.cursor == 0
        print("PASS: command record pool sparse clear and cursor reset")


if __name__ == "__main__":
    main()
