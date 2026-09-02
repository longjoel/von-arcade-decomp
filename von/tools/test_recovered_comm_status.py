#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_comm_status.c"

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "comm-status.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(source)], check=True)
    lib = ctypes.CDLL(str(library))
    role = lib.recovered_comm_role_message
    role.argtypes = [ctypes.c_uint8]
    role.restype = ctypes.c_int
    assert [role(value) for value in range(6)] == [0, 1, 2, 3, 4, 4]

    present = lib.recovered_comm_board_present
    present.argtypes = [ctypes.c_uint8]
    present.restype = ctypes.c_uint8
    assert [present(value) for value in (0x00, 0x01, 0x80, 0xff)] == [1, 0, 1, 0]

    reset = lib.recovered_comm_control_reset
    reset.argtypes = [ctypes.POINTER(ctypes.c_uint8)]
    control_bytes = (ctypes.c_uint8 * 2)(0xa5, 0x5a)
    reset(control_bytes)
    assert list(control_bytes) == [0, 0]

print("recovered communication-status vectors: ok")
