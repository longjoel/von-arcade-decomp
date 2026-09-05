#!/usr/bin/env python3
"""Contract test for the texture loader's shared outcome/state boundary."""

from pathlib import Path
import ctypes
import os
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_texture.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-texture-loader-result-") as directory:
        directory = Path(directory)
        stubs = directory / "stubs.c"
        stubs.write_text(
            "typedef unsigned int u32; typedef unsigned short u16; typedef unsigned char u8;\n"
            "int recovered_texture_decompress(volatile const u8 *a, volatile u16 *b, volatile u16 *c) { (void)a; (void)b; (void)c; return 0; }\n"
            "void recovered_text_set_position(u32 a, u32 b) { (void)a; (void)b; }\n"
            "void recovered_text_write_string(volatile const u8 *a) { (void)a; }\n",
            encoding="utf-8",
        )
        library = directory / "texture.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", str(SOURCE),
             str(stubs), "-o", str(library)],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        result = recovered.recovered_texture_loader_profile_result
        result.argtypes = [
            ctypes.c_int, ctypes.c_int,
            ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint)]
        result.restype = ctypes.c_int

        vectors = ((0, 0, 0), (7, 0, 7), (0, -3, -3), (5, -9, 5))
        for first_status, second_status, expected_status in vectors:
            state_a = ctypes.c_uint(0xDEADBEEF)
            state_b = ctypes.c_uint(0xDEADBEEF)
            actual = result(
                first_status, second_status,
                ctypes.byref(state_a), ctypes.byref(state_b))
            if actual != expected_status:
                raise SystemExit(
                    f"loader result mismatch: {actual} != {expected_status}"
                )
            if expected_status == 0:
                if (state_a.value, state_b.value) != (0xDEADBEEF, 0xDEADBEEF):
                    raise SystemExit("successful loader changed failure state")
            elif (state_a.value, state_b.value) != (5, 0):
                raise SystemExit("failed loader state contract mismatch")

    print(f"PASS: {len(vectors)} texture loader outcome/state vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
