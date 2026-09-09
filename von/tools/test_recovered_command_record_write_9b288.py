#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Record(ctypes.Structure):
    _fields_ = [("active", ctypes.c_uint8), ("reserved", ctypes.c_uint8),
                ("value_2", ctypes.c_uint16), ("value_4", ctypes.c_uint32),
                ("value_8", ctypes.c_uint32), ("value_c", ctypes.c_uint32)]


class Table(ctypes.Structure):
    _fields_ = [("record", Record * 16), ("cursor", ctypes.c_uint32)]


class Input(ctypes.Structure):
    _fields_ = [("value_8", ctypes.c_uint16), ("value_10", ctypes.c_uint32),
                ("value_14", ctypes.c_uint32), ("value_18", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-command-record-write-") as d:
        so = Path(d) / "command-record-write.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        str(ROOT / "von/i960/recovered_command_record_write_9b288.c"),
                        "-o", str(so)], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_command_record_write_9b288
        fn.argtypes = [ctypes.POINTER(Table), ctypes.POINTER(Input)]
        state = Table()
        ctypes.memset(ctypes.byref(state), 0xa5, ctypes.sizeof(state))
        state.cursor = 0x23
        input_value = Input(0x1234, 0x55667788, 0x99aabbcc, 0xddeeff00)
        fn(ctypes.byref(state), ctypes.byref(input_value))
        assert state.cursor == 4
        assert (state.record[3].active, state.record[3].reserved) == (1, 0)
        assert state.record[3].value_2 == 0x1234
        assert (state.record[3].value_4, state.record[3].value_8,
                state.record[3].value_c) == (0x55667788, 0x99aabbcc, 0xddeeff00)
        assert state.record[4].active == 0xa5
        print("PASS: command record low-nibble write and cursor advance")


if __name__ == "__main__":
    main()
