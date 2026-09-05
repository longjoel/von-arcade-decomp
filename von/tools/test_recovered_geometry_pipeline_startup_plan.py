#!/usr/bin/env python3
"""Contract test for the recovered geometry startup helper order and mode gate."""

from pathlib import Path
import ctypes
import os
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_commands.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-geometry-startup-plan-") as directory:
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
        plan = recovered.recovered_geometry_pipeline_startup_plan
        plan.argtypes = [ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong)]
        plan.restype = ctypes.c_ulong

        expected = {
            0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11),
            1: (1, 4, 5, 6, 7, 8, 10, 11),
            0xFFFFFFFF: (1, 4, 5, 6, 7, 8, 10, 11),
        }
        for mode, wanted in expected.items():
            steps = (ctypes.c_ulong * 11)()
            count = plan(mode, steps)
            if tuple(steps[:count]) != wanted:
                raise SystemExit(
                    f"startup plan mismatch mode={mode:#x}: "
                    f"{tuple(steps[:count])!r} != {wanted!r}"
                )

    print(f"PASS: {len(expected)} geometry startup mode plans")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
