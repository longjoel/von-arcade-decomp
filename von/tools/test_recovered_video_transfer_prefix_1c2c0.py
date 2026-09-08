#!/usr/bin/env python3
"""Validate the bounded video-transfer prefix at i960 0x1c2c0."""
import ctypes
import pathlib
import subprocess
import tempfile


class Prefix(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "saved_argument_quadword", "saved_context_quadword",
        "stack_frame_bytes", "saved_g13", "saved_g14", "fp_register_count",
        "workspace_base", "workspace_halfword_count", "metadata_base")]


root = pathlib.Path(__file__).parents[2]
with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "prefix.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(root / "von/i960/recovered_video_transfer_prefix_1c2c0.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    prefix = lib.recovered_video_transfer_prefix_1c2c0
    prefix.argtypes = [ctypes.POINTER(Prefix)]
    out = Prefix()
    prefix(ctypes.byref(out))
    actual = tuple(getattr(out, name) for name, _ in Prefix._fields_)
    if actual != (1, 1, 0x50, 1, 1, 4, 0x01008000, 512, 0x0100A000):
        raise SystemExit("1c2c0 workspace prefix mismatch")

    rebase = lib.recovered_video_transfer_rebase_1c2c0
    rebase.argtypes = [ctypes.POINTER(ctypes.c_int16), ctypes.c_int16,
                       ctypes.POINTER(ctypes.c_int16), ctypes.c_uint32]
    source = (ctypes.c_int16 * 512)(*[index - 256 for index in range(512)])
    destination = (ctypes.c_int16 * 512)()
    if rebase(source, 7, destination, 512) != 512:
        raise SystemExit("1c2c0 rebase count mismatch")
    if list(destination) != [index - 249 for index in range(512)]:
        raise SystemExit("1c2c0 rebase values mismatch")

print("PASS: 0x1c2c0 video-transfer prefix")
