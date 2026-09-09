#!/usr/bin/env python3
import ctypes, os, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
class Result(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "reset_call", "reset_argument", "phase_helper_call", "phase_helper_argument",
        "ready_address", "ready_before", "ready_path", "phase_source_address",
        "phase_source_value")]
    _fields_ += [("workspace_clear_address", ctypes.c_uint32 * 3), ("workspace_clear_count", ctypes.c_uint32), ("workspace_copy_address", ctypes.c_uint32 * 3), ("workspace_copy_count", ctypes.c_uint32)]
    _fields_ += [(n, ctypes.c_uint32) for n in ("maintenance_call", "marker_address", "marker_value", "profile_table_address", "profile_table_index", "status_byte_address", "status_byte", "status_mask", "status_lookup_address", "status_lookup_value", "status_publication_address", "status_publication_value", "secondary_status_address", "secondary_status_value", "secondary_publication_address", "secondary_publication_value")]
    _fields_ += [("record_publication_address", ctypes.c_uint32 * 3), ("record_publication_count", ctypes.c_uint32)]
    _fields_ += [(n, ctypes.c_uint32) for n in ("phase_address", "phase_before", "phase_after", "return_target")]

with tempfile.TemporaryDirectory(prefix="von-startup-arm-19830-") as directory:
    so = Path(directory) / "x.so"
    subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", "-I", str(ROOT / "von/i960"), "-o", str(so), str(ROOT / "von/i960/recovered_startup_mode4_arm_19830.c")], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_mode4_arm_19830
    fn.argtypes = [ctypes.c_uint32] * 5 + [ctypes.POINTER(Result)]
    out = Result(); fn(0, 4, 0xff, 0x777, 0x12, ctypes.byref(out))
    assert (out.ready_path, out.status_byte_address, out.status_publication_value, out.secondary_status_address, out.marker_value, out.phase_after, out.return_target) == (0, 0x1d0001a, 0xf423f, 0x1d0001f, 0xff, 5, 0x19b4c)
    fn(1, 4, 3, 0x777, 0x22, ctypes.byref(out))
    assert (out.ready_path, out.status_byte_address, out.status_publication_value, out.secondary_status_address, out.secondary_publication_value, out.phase_after) == (1, 0x1d00016, 0x777, 0x1d0001b, 0x22, 5)
print("PASS: 0x19830 startup phase-table arm")
