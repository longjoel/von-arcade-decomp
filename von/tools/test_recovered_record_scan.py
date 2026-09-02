#!/usr/bin/env python3
import ctypes
import pathlib
import random
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_record_scan.c"


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "record_scan.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
        dll = ctypes.CDLL(str(library))
        scan = dll.recovered_record_find_last_nonempty
        scan.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_uint]
        scan.restype = ctypes.c_int

        rng = random.Random(0xBF0C0)
        for count in range(0, 65):
            records = (ctypes.c_ubyte * max(1, count * 32))()
            occupied = []
            for slot in range(count):
                if rng.randrange(4) == 0:
                    records[slot * 32] = rng.randrange(1, 256)
                    occupied.append(slot)
                records[slot * 32 + 17] = 0xA5
            assert scan(records, count) == (occupied[-1] if occupied else -1)

        records = (ctypes.c_ubyte * 96)()
        records[0], records[32], records[64] = 1, 2, 3
        assert scan(records, 3) == 2
        assert scan(records, 2) == 1
        assert scan(records, 1) == 0

    print("recovered fixed-record scan vectors: ok")


if __name__ == "__main__":
    main()
