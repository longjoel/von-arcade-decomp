#!/usr/bin/env python3
"""Contract test for the recovered geometry startup handshake writes."""

from pathlib import Path
import ctypes
import os
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_commands.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-geometry-handshake-") as directory:
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
        ulong = ctypes.c_ulong
        recovered.recovered_geometry_initial_handshake_plan.argtypes = [
            ctypes.POINTER(ulong), ctypes.POINTER(ulong), ctypes.POINTER(ulong),
            ctypes.POINTER(ulong), ctypes.POINTER(ulong)]
        recovered.recovered_geometry_initial_handshake_plan.restype = None

        control = ulong(0xDEADBEEF)
        write_start = ulong(0xDEADBEEF)
        command_window = (ulong * 0x40)(*([0xDEADBEEF] * 0x40))
        read_start = ulong(0xDEADBEEF)
        phase = ulong(0xDEADBEEF)
        recovered.recovered_geometry_initial_handshake_plan(
            ctypes.byref(control), ctypes.byref(write_start), command_window,
            ctypes.byref(read_start), ctypes.byref(phase))

        if control.value != 0 or write_start.value != 0x10000:
            raise SystemExit("control/write-start handshake mismatch")
        if command_window[0x0F0 // 4] != 0x0F0F:
            raise SystemExit("command-window handshake marker mismatch")
        if read_start.value != 0x10000 or phase.value != 0:
            raise SystemExit("read-start/phase handshake mismatch")
        if any(value != 0xDEADBEEF for value in command_window[:0x0F0 // 4]):
            raise SystemExit("handshake touched an unrelated command-window field")

    print("PASS: seven geometry handshake writes and marker placement")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
