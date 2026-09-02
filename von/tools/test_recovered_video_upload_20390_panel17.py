#!/usr/bin/env python3
"""Test the 0x20390 upload and 0x203b0 panel helper contracts."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_video_upload_20390_panel17.c"


class Upload(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("source", "destination", "flags", "halfwords_per_row", "rows", "helper")]


class Panel(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("source", "helper", "column_comes_from_current_position",
                 "row_comes_from_current_position", "width", "height")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-upload-20390-") as directory:
        library = Path(directory) / "upload-20390.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        upload_fn = recovered.recovered_upload_20390_plan
        upload_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Upload)]
        upload = Upload()
        upload_fn(17, ctypes.byref(upload))
        assert (upload.source, upload.destination, upload.flags,
                upload.halfwords_per_row, upload.rows, upload.helper) == (0x1004000, 0x1FCCD20,
                                                                         0x40, 0x40, 48, 0x1BC90)

        panel_fn = recovered.recovered_panel17_plan
        panel_fn.argtypes = [ctypes.POINTER(Panel)]
        panel = Panel()
        panel_fn(ctypes.byref(panel))
        assert (panel.source, panel.helper, panel.column_comes_from_current_position,
                panel.row_comes_from_current_position, panel.width, panel.height) == (0x2FE0864, 0x1DC90, 1, 1, 31, 5)

    print("PASS: 0x20390 upload/0x203b0 panel helpers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
