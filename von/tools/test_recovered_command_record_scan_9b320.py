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
    _fields_ = [("record", Record * 16)]


class Result(ctypes.Structure):
    _fields_ = [("selected_index", ctypes.c_uint32 * 16),
                ("fifo_prefix", (ctypes.c_uint32 * 7) * 16),
                ("selected_count", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-command-record-scan-") as d:
        so = Path(d) / "command-record-scan.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        str(ROOT / "von/i960/recovered_command_record_scan_9b320.c"),
                        "-o", str(so)], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_command_record_scan_9b320
        fn.argtypes = [ctypes.POINTER(Table), ctypes.POINTER(Result)]
        state = Table()
        ctypes.memset(ctypes.byref(state), 0, ctypes.sizeof(state))
        state.record[0].active = 0
        state.record[1].active = 1
        state.record[1].value_4 = 0xa5a5a5a5
        state.record[1].reserved = 0x12
        state.record[1].value_2 = 0x3456
        state.record[1].value_8 = 0x11223344
        state.record[1].value_c = 0x55667788
        state.record[2].active = 0x20
        state.record[3].active = 0x80
        state.record[4].value_4 = 0xa5a5a5a5
        result = Result()
        fn(ctypes.byref(state), ctypes.byref(result))
        assert result.selected_count == 3
        assert list(result.selected_index[:3]) == [1, 2, 3]
        assert list(result.fifo_prefix[0]) == [5, 18, 0xa5a5a5a5,
                                               0x11223344, 0x55667788,
                                               21, 0x5612]
        assert [state.record[i].active for i in range(4)] == [0, 0, 0x21, 0x81]
        assert state.record[4].active == 0
        assert state.record[1].value_4 == 0xa5a5a5a5
        print("PASS: command record scan selection and active-state transition")


if __name__ == "__main__":
    main()
