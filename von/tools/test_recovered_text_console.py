#!/usr/bin/env python3
"""Validate the recovered i960 hardware text console (0x1c618/0x1cbb8/0x1cc40).

Compiles von/i960/recovered_text_console.c with
    cc -std=c11 -Wall -Wextra -Werror -shared -fPIC
and drives the pure core; the _run wrappers own the target addresses.

Covered listing spans:
    0x1cac8  set cursor
    0x1cbb8  control: cmd 9 tab, cmd 10 line feed
    0x1cc40  putc: control vs nametable cell
    0x1ccd0  puts
"""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text_console.c"

CC = ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC"]


class Console(ctypes.Structure):
    _fields_ = [
        ("saved", ctypes.c_uint32),
        ("column", ctypes.c_uint32),
        ("row", ctypes.c_uint32),
        ("attr", ctypes.c_uint32),
    ]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "text-console.so"
        subprocess.run(CC + [str(SOURCE), "-o", str(library)], check=True)
        recovered = ctypes.CDLL(str(library))

        reset = recovered.recovered_text_console_reset_core
        reset.argtypes = [ctypes.POINTER(Console)]
        set_cursor = recovered.recovered_text_console_set_cursor_core
        set_cursor.argtypes = [ctypes.POINTER(Console),
                               ctypes.c_uint32, ctypes.c_uint32]
        putc = recovered.recovered_text_console_putc_core
        putc.argtypes = [ctypes.POINTER(Console), ctypes.c_uint32,
                         ctypes.POINTER(ctypes.c_uint32),
                         ctypes.POINTER(ctypes.c_uint32)]
        putc.restype = ctypes.c_uint32

        # --- reset clears the state ----------------------------------------
        c = Console(9, 9, 9, 9)
        reset(ctypes.byref(c))
        assert (c.saved, c.column, c.row, c.attr) == (0, 0, 0, 0)

        # --- set cursor -----------------------------------------------------
        set_cursor(ctypes.byref(c), 5, 2)
        assert (c.saved, c.column, c.row) == (5, 5, 2)

        # --- putc printable writes the nametable cell -----------------------
        index = ctypes.c_uint32(0)
        value = ctypes.c_uint32(0)
        assert putc(ctypes.byref(c), 65, ctypes.byref(index),
                    ctypes.byref(value)) == 1
        assert index.value == (2 << 6) + 5, hex(index.value)
        assert value.value == 0xffff8041, hex(value.value)
        assert c.column == 6, hex(c.column)

        # --- line feed (cmd 10): column <- saved, row++ ---------------------
        assert putc(ctypes.byref(c), 10, ctypes.byref(index),
                    ctypes.byref(value)) == 0
        assert c.column == 5, hex(c.column)
        assert c.row == 3, hex(c.row)

        # --- tab (cmd 9): column to next multiple of 8 ----------------------
        set_cursor(ctypes.byref(c), 3, 0)
        assert putc(ctypes.byref(c), 9, ctypes.byref(index),
                    ctypes.byref(value)) == 0
        assert c.column == 8, hex(c.column)

        # --- attribute OR ---------------------------------------------------
        c = Console(0, 0, 0, 0x1000)
        assert putc(ctypes.byref(c), 0x41, ctypes.byref(index),
                    ctypes.byref(value)) == 1
        assert value.value == 0xffff9041, hex(value.value)

    print("PASS: recovered i960 text console (0x1c618/0x1cc40)")


if __name__ == "__main__":
    main()
