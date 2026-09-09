#!/usr/bin/env python3
import ctypes
import os
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Tables(ctypes.Structure):
    _fields_ = [("table_5050a0", (ctypes.c_uint16 * (0x90 // 2)) * 64),
                ("table_5074a0", (ctypes.c_uint16 * (0x88 // 2)) * 64)]


def main():
    listing = LISTING.read_text()
    for instruction in (r"866c0:.*lda.*0x5050a0",
                        r"866c8:.*addo.*31,28,r6",
                        r"86724:.*addo.*g2,20,g0",
                        r"866e8:.*stos.*g14",
                        r"86748:.*stos.*g14",
                        r"86810:.*lda.*0x440\(r4\)",
                        r"8681c:.*cmpi.*r4,r7"):
        assert re.search(instruction, listing)

    with tempfile.TemporaryDirectory(prefix="von-stage-record-tables-") as d:
        so = Path(d) / "stage-record-tables.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        str(ROOT / "von/i960/recovered_stage_record_tables_866c0.c"),
                        "-o", str(so)], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_stage_record_tables_write_plan_866c0
        fn.argtypes = [ctypes.POINTER(Tables), ctypes.c_uint16]
        state = Tables()
        ctypes.memset(ctypes.byref(state), 0xa5, ctypes.sizeof(state))
        fn(ctypes.byref(state), 0x1234)
        for record in range(64):
            a = state.table_5050a0[record]
            assert list(a[:10]) == [0x1234] * 10
            assert list(a[10:69]) == [0x1234] * 59
            assert (a[69], a[70], a[71]) == (0xa5a5, 0x1234, 0x1234)
            b = state.table_5074a0[record]
            assert list(b[:65]) == [0x1234] * 65
            assert (b[65], b[66], b[67]) == (0xa5a5, 0xa5a5, 0x1234)
        print("PASS: stage record table sparse write plan")


if __name__ == "__main__":
    main()
