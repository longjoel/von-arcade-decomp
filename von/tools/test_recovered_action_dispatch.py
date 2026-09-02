#!/usr/bin/env python3
"""Check the recovered 0x77e60 action-dispatch table."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_action_dispatch.c"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "libaction_dispatch.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
        api = ctypes.CDLL(str(library))
        function = api.recovered_action_dispatch_target
        function.argtypes = [ctypes.c_uint32]
        function.restype = ctypes.c_uint32

        expected = [
            0x77f2c, 0x77f34, 0x77f3c, 0x77f44, 0x77f4c, 0x77f54,
            0x77f5c, 0x77f64, 0x77f6c, 0x77f7c, 0x77f84, 0x77f74,
            0x78084, 0x77f8c, 0x77f94, 0x77f9c, 0x77fa4, 0x77fac,
            0x77fb4, 0x77fbc, 0x77fc4, 0x77fcc, 0x77fd4, 0x77fdc,
            0x77fe4, 0x77fec, 0x77ff4, 0x77ffc, 0x78004, 0x7800c,
            0x78014, 0x7801c, 0x78024, 0x7802c, 0x78034, 0x7803c,
            0x78044, 0x7804c, 0x78054, 0x7805c, 0x78064, 0x7806c,
            0x78074, 0x7807c,
        ]
        assert [function(index) for index in range(44)] == expected
        assert function(44) == 0x78084
        assert function(0xffffffff) == 0x78084

    print("recovered action-dispatch vectors: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
