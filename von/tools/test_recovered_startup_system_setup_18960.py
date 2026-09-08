#!/usr/bin/env python3
"""Validate the ordered startup service wrapper at i960 0x18960."""
import ctypes
import pathlib
import subprocess
import tempfile


class Setup(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "io_self_test", "video_control_bootstrap", "startup_asset_transfer",
        "audio_table_clear", "text_position_set", "status_string_kind",
        "geometry_startup", "stage_latch_published", "audio_queue_initialize",
        "video_dispatch", "audio_buffer_copy", "audio_service_reset",
        "stage_record_tables", "continuation_thunk", "io_wrapper",
        "host_queue_initialize")]


root = pathlib.Path(__file__).parents[2]
with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "setup.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(root / "von/i960/recovered_startup_system_setup_18960.c"),
                    "-o", str(so)], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_system_setup_18960
    fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Setup)]
    for result, kind in ((0, 0), (1, 1), (2, 2), (0xFFFFFFFF, 2)):
        out = Setup()
        fn(result, 0x1234, ctypes.byref(out))
        values = tuple(getattr(out, name) for name, _ in Setup._fields_)
        if values[5] != kind or any(value != 1 for value in values[:5] + values[6:]):
            raise SystemExit("0x18960 startup setup mismatch")

print("PASS: 0x18960 startup system setup plan")
