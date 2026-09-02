#!/usr/bin/env python3
"""Validate the composed opcode-0x17 selection and plane-result model."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCES = (
    ROOT / "von/i960/recovered_sharc_opcode_17.c",
    ROOT / "von/i960/recovered_sharc_opcode_17_projection.c",
    ROOT / "von/i960/recovered_sharc_helper_20de1.c",
    ROOT / "von/i960/recovered_sharc_opcode_35.c",
)


def word(value):
    return ctypes.c_uint32.from_buffer_copy(ctypes.c_float(value)).value


def main() -> int:
    record = [word(value) for point in ((1, 2, 5), (4, 7, 6), (9, 8, 3), (10, 11, 12))
              for value in point]
    with tempfile.TemporaryDirectory(prefix="von-sharc-17-projection-") as directory:
        library_path = pathlib.Path(directory) / "projection.so"
        subprocess.run(["cc", "-std=c99", "-shared", "-fPIC", "-O2",
                        *(str(source) for source in SOURCES), "-o", str(library_path)],
                       check=True)
        library = ctypes.CDLL(str(library_path))
        project = library.recovered_sharc_opcode_17_project_record
        project.argtypes = [
            ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32, ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32), ctypes.c_size_t,
            ctypes.c_float, ctypes.c_float,
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_uint32),
        ]
        project.restype = ctypes.c_int
        selectors = (ctypes.c_uint32 * 1)(0)
        bank = (ctypes.c_uint32 * 12)(*record)
        staged = (ctypes.c_uint32 * 12)()
        determinant = ctypes.c_float()
        result = ctypes.c_uint32()

        for x, z, expected in (
            (0.0, 0.0, 0xbcdd67c8),
            (0.25, 0.25, 0x3e722983),
            (0.5, 0.5, 0x3f000000),
            (1.0, 1.0, 0x3f83759f),
            (-1.0, -1.0, 0xbf8a60dd),
            (0.25, 0.5, 0x3e983759),
            (0.5, 0.25, 0x3ee0dd67),
            (2.0, 2.0, 0x4005306e),
        ):
            status = project(selectors, 1, 0, bank, 12, x, z, staged,
                             ctypes.byref(determinant), ctypes.byref(result))
            if status != 1 or result.value != expected:
                raise SystemExit(f"projection {x}/{z} was {result.value:#x}, expected {expected:#x}")

        status = project(selectors, 1, 0, bank, 12, 4.0, 6.0, staged,
                         ctypes.byref(determinant), ctypes.byref(result))
        if status != 0:
            raise SystemExit("zero-determinant caller gate was not preserved")

    print("recovered SHARC opcode-0x17 composed projection vectors: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
