#!/usr/bin/env python3
"""Contract test for the recovered 64-slot command-window clear loop."""

from pathlib import Path
import ctypes
import os
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_commands.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-command-clear-") as directory:
        directory = Path(directory)
        stubs = directory / "stubs.c"
        stubs.write_text(
            "typedef unsigned int u32; typedef unsigned short u16;\n"
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
        recovered.recovered_geometry_command_window_clear_slots.argtypes = [
            ctypes.POINTER(ctypes.c_ulong), ctypes.c_ulong]
        recovered.recovered_geometry_command_window_clear_slots.restype = None

        slots = 64
        window = (ctypes.c_ulong * (slots * 4 + 1))(
            *([0xDEADBEEF] * (slots * 4 + 1))
        )
        recovered.recovered_geometry_command_window_clear_slots(window, slots)
        for slot in range(slots):
            if window[slot * 4 + 1] != 0 or window[slot * 4 + 2] != 0:
                raise SystemExit(f"clear mismatch at slot {slot}")
            if window[slot * 4] != 0xDEADBEEF or window[slot * 4 + 3] != 0xDEADBEEF:
                raise SystemExit(f"clear overwrote unrelated field at slot {slot}")
        if window[slots * 4] != 0xDEADBEEF:
            raise SystemExit("clear exceeded the declared slot count")

    print(f"PASS: {slots} command slots cleared without touching adjacent fields")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
