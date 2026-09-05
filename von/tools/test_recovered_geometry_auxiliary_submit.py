#!/usr/bin/env python3
"""Contract test for the recovered auxiliary geometry source/count selector."""

from pathlib import Path
import ctypes
import os
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_commands.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-geometry-auxiliary-") as directory:
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
        plan = recovered.recovered_geometry_auxiliary_submit_plan
        plan.argtypes = [
            ctypes.c_ulong, ctypes.c_ulong,
            ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.c_ulong)]
        plan.restype = None

        vectors = (
            (4, 32, 0x001687A4, 0x4E4),
            (4, 31, 0x001686E4, 0x60),
            (3, 32, 0x001686E4, 0x60),
            (0xFFFFFFFF, 0xFFFFFFFF, 0x001686E4, 0x60),
        )
        for state_a, state_b, expected_source, expected_count in vectors:
            source = ctypes.c_ulong()
            count = ctypes.c_ulong()
            plan(state_a, state_b, ctypes.byref(source), ctypes.byref(count))
            if (source.value, count.value) != (expected_source, expected_count):
                raise SystemExit(
                    f"auxiliary plan mismatch ({state_a:#x}, {state_b:#x}): "
                    f"{source.value:#x}, {count.value:#x}"
                )

    print(f"PASS: {len(vectors)} auxiliary geometry submit selector vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
