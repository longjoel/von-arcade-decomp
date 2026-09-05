#!/usr/bin/env python3
"""Contract test for the recovered 32-bit geometry batch header."""

from pathlib import Path
import ctypes
import os
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_commands.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-geometry-batch-header-") as directory:
        directory = Path(directory)
        stubs = directory / "stubs.c"
        stubs.write_text(
            "typedef unsigned long u32; typedef unsigned short u16;\n"
            "void recovered_geometry_buffer_prepare(volatile u32 *p) { (void)p; }\n"
            "void recovered_geometry_matrix_submission(void) {}\n"
            "u32 recovered_geometry_object_profile_submission(const u32 *a, const u32 *b, u32 c, u32 d, u32 *e) { (void)a; (void)b; (void)c; (void)d; (void)e; return 0; }\n"
            "void recovered_geometry_polygon_object_submission(u32 a, u32 b, u32 c, u32 d, u32 *e) { (void)a; (void)b; (void)c; (void)d; (void)e; }\n"
            "void recovered_geometry_profile_setup(void) {}\n"
            "void recovered_geometry_program_upload(void) {}\n"
            "void recovered_sharc_bootstrap_upload(void) {}\n"
            "void recovered_texture_initializer(void) {}\n",
            encoding="utf-8",
        )
        library = directory / "geometry.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", str(SOURCE),
             str(stubs), "-o", str(library)],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        header = recovered.recovered_geometry_batch_command_header
        header.argtypes = [
            ctypes.c_ulong, ctypes.c_ulong,
            ctypes.POINTER(ctypes.c_ulong)]
        header.restype = None

        vectors = ((0x12345678, 0x800), (0xFFFFFFFF, 0), (0x00018000, 7))
        for command, count in vectors:
            output = (ctypes.c_ulong * 2)()
            header(command, count, output)
            expected = (command & 0xFFFF, count)
            if tuple(output) != expected:
                raise SystemExit(
                    f"batch header mismatch: {tuple(output)!r} != {expected!r}"
                )

    print(f"PASS: {len(vectors)} geometry batch header vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
