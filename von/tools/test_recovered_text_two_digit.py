#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text_two_digit.c"


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "two_digit.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
        dll = ctypes.CDLL(str(library))
        emit = dll.recovered_text_two_digit
        emit.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte)]
        emit.restype = ctypes.c_int
        for value, expected in ((0, b"00"), (9, b"09"), (42, b"42"), (99, b"99"), (100, b"99")):
            out = (ctypes.c_ubyte * 2)()
            assert emit(value, out) == 1
            assert bytes(out) == expected
        out = (ctypes.c_ubyte * 2)()
        assert emit(-1, out) == 0
    print("recovered two-digit formatter vectors: ok")


if __name__ == "__main__":
    main()
