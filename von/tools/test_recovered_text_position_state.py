#!/usr/bin/env python3
"""Contract test for the recovered text origin/column/row setter."""

from pathlib import Path
import ctypes
import os
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-text-position-") as directory:
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
        ulong = ctypes.c_uint32
        recovered.recovered_text_set_position_state.argtypes = [
            ctypes.POINTER(ulong), ctypes.POINTER(ulong), ctypes.POINTER(ulong),
            ulong, ulong]
        recovered.recovered_text_set_position_state.restype = None

        origin = ulong(0xDEADBEEF)
        column = ulong(0xDEADBEEF)
        row = ulong(0xDEADBEEF)
        recovered.recovered_text_set_position_state(
            ctypes.byref(origin), ctypes.byref(column), ctypes.byref(row),
            37, 23)
        if (origin.value, column.value, row.value) != (37, 37, 23):
            raise SystemExit("text position state mismatch")

    print("PASS: text origin, column, and row state update")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
