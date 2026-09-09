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
        "host_queue_initialize", "stage_latch_before", "stage_latch_after",
        "stage_latch_initialize_call", "call_count")] + [
            ("call_targets_%d" % i, ctypes.c_uint32) for i in range(16)]


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
        if values[5] != kind or any(value != 1 for value in values[:5] + values[6:16]):
            raise SystemExit("0x18960 startup setup mismatch")

    out = Setup()
    fn(0, 0x1234, ctypes.byref(out))
    assert (out.stage_latch_before, out.stage_latch_after,
            out.stage_latch_initialize_call, out.call_count) == (0x1234, 1, 0, 15)
    assert tuple(getattr(out, "call_targets_%d" % i) for i in range(15)) == (
        0x2730, 0x1c220, 0x1bda0, 0x29a80, 0x1cac8, 0x1da90,
        0x2a8a0, 0xe2130, 0x29ca0, 0x29ae8, 0xbd5a8, 0x866c0,
        0x18918, 0x2440, 0x1bb8)
    out = Setup()
    fn(0, 0, ctypes.byref(out))
    assert (out.stage_latch_initialize_call, out.call_count,
            getattr(out, "call_targets_6")) == (1, 16, 0x28d80)

print("PASS: 0x18960 startup system setup plan")
