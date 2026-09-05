#!/usr/bin/env python3
"""Contract test for the recovered NUL-terminated text byte walk."""

from pathlib import Path
import ctypes
import os
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-text-string-") as directory:
        directory = Path(directory)
        stubs = directory / "stubs.c"
        stubs.write_text(
            "typedef unsigned int u32; typedef unsigned short u16; "
            "typedef unsigned char u8;\n"
            "void recovered_memory_copy_forward(volatile u8 *a, "
            "volatile const u8 *b, u32 c) { (void)a; (void)b; (void)c; }\n"
            "void recovered_host_fatal_halt(void) {}\n",
            encoding="utf-8",
        )
        library = directory / "text.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", str(SOURCE),
             str(stubs), "-o", str(library)],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        recovered.recovered_text_string_length.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte)]
        recovered.recovered_text_string_length.restype = ctypes.c_uint32

        vectors = (b"\x00", b"READY\x00", b"A\x00ignored", bytes(range(1, 64)) + b"\x00")
        for value in vectors:
            text = (ctypes.c_ubyte * len(value))(*value)
            expected = value.index(0) if 0 in value else len(value)
            actual = recovered.recovered_text_string_length(text)
            if actual != expected:
                raise SystemExit(
                    f"string length mismatch for {value!r}: {actual} != {expected}"
                )

    print(f"PASS: {len(vectors)} NUL-terminated text length vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
