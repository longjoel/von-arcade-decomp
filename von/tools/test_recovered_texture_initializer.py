#!/usr/bin/env python3
"""Contract test for the deterministic texture initializer tables."""

from pathlib import Path
import ctypes
import os
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_texture.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-texture-init-") as directory:
        directory = Path(directory)
        stubs = directory / "stubs.c"
        stubs.write_text(
            "typedef unsigned int u32; typedef unsigned short u16; "
            "typedef unsigned char u8;\n"
            "int recovered_texture_decompress(const volatile u8 *a, "
            "volatile u16 *b, volatile u16 *c) { (void)a; (void)b; (void)c; return 0; }\n"
            "void recovered_text_set_position(u32 a, u32 b) { (void)a; (void)b; }\n"
            "void recovered_text_write_string(const volatile u8 *a) { (void)a; }\n",
            encoding="utf-8",
        )
        library = directory / "texture-init.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", str(SOURCE),
             str(stubs), "-o", str(library)],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        recovered.recovered_texture_initialize_tables.argtypes = [
            ctypes.POINTER(ctypes.c_uint16),
            ctypes.POINTER(ctypes.c_uint16),
            ctypes.POINTER(ctypes.c_ubyte),
        ]
        recovered.recovered_texture_initialize_tables.restype = None

        ramp = (ctypes.c_uint16 * (0x7F * 2))(*([0xBEEF] * (0x7F * 2)))
        table = (ctypes.c_uint16 * 0x2080)(*([0xBEEF] * 0x2080))
        source = (ctypes.c_ubyte * 0x2080)(
            *(((index * 37) + 11) & 0xFF for index in range(0x2080))
        )
        recovered.recovered_texture_initialize_tables(ramp, table, source)

        for index in range(0x7F * 2):
            expected = (index % 0x7F + 1) >> 1
            if ramp[index] != expected:
                raise SystemExit(
                    f"ramp mismatch index={index}: {ramp[index]} != {expected}"
                )
        for index in range(0x2080):
            if table[index] != source[index]:
                raise SystemExit(
                    f"table mismatch index={index}: {table[index]} != {source[index]}"
                )

    print("PASS: 254 ramp entries and 8,320 texture table halfwords")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
