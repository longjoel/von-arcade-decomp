#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Tables(ctypes.Structure):
    _fields_ = [("table_5050a0", (ctypes.c_uint16 * (0x90 // 2)) * 8),
                ("table_5074a0", (ctypes.c_uint16 * (0x88 // 2)) * 8)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-stage-record-tables-") as d:
        so = Path(d) / "stage-record-tables.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        str(ROOT / "von/i960/recovered_stage_record_tables_866c0.c"),
                        "-o", str(so)], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_stage_record_tables_write_plan_866c0
        fn.argtypes = [ctypes.POINTER(Tables)]
        state = Tables()
        ctypes.memset(ctypes.byref(state), 0xa5, ctypes.sizeof(state))
        fn(ctypes.byref(state))
        for record in range(8):
            a = state.table_5050a0[record]
            assert list(a[:10]) == [0] * 10
            assert list(a[10:69]) == [0] * 59
            assert (a[69], a[70], a[71]) == (0xa5a5, 0, 0)
            b = state.table_5074a0[record]
            assert list(b[:65]) == [0] * 65
            assert (b[65], b[66], b[67]) == (0xa5a5, 0xa5a5, 0)
        print("PASS: stage record table sparse write plan")


if __name__ == "__main__":
    main()
