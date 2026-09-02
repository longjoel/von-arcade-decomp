#!/usr/bin/env python3
"""Test the 0x20460 upload and 0x20480 panel route contracts."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_upload_20460_panel18.c"


class Upload(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("source", "destination", "flags", "halfwords_per_row", "rows", "helper")]


class Panel(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("source", "source_helper", "fill_helper", "column_advance", "width", "height")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-upload-20460-") as directory:
        library = Path(directory) / "upload-20460.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        upload_fn = recovered.recovered_upload_20460_plan
        upload_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Upload)]
        upload = Upload()
        upload_fn(17, ctypes.byref(upload))
        assert (upload.source, upload.destination, upload.flags,
                upload.halfwords_per_row, upload.rows, upload.helper) == (0x1004000, 0x1FD89D0,
                                                                         0x40, 0x40, 48, 0x1BC90)

        panel_fn = recovered.recovered_panel18_plan
        panel_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Panel)]
        panel = Panel()
        panel_fn(1, ctypes.byref(panel))
        assert (panel.source, panel.source_helper, panel.fill_helper,
                panel.column_advance, panel.width, panel.height) == (0x2FCF468, 0x1DC10, 0, 4, 8, 4)
        panel_fn(0, ctypes.byref(panel))
        assert (panel.source, panel.source_helper, panel.fill_helper) == (0, 0, 0x1DF00)

    print("PASS: 0x20460 upload/0x20480 panel route")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
