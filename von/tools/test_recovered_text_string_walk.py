#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text_string_walk.c"
EMIT = ctypes.CFUNCTYPE(None, ctypes.c_ubyte, ctypes.c_void_p)


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "string_walk.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
        dll = ctypes.CDLL(str(library))
        walk = dll.recovered_text_string_walk
        walk.argtypes = [ctypes.c_char_p, EMIT, ctypes.c_void_p]
        seen = []

        @EMIT
        def emit(value, _opaque):
            seen.append(value)

        walk(b"WIN\n", emit, None)
        assert seen == [ord("W"), ord("I"), ord("N"), ord("\n")]
        seen.clear()
        walk(b"", emit, None)
        assert seen == []
    print("recovered text string walker vectors: ok")


if __name__ == "__main__":
    main()
