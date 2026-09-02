#!/usr/bin/env python3
import ctypes
import pathlib
import struct
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_coordinate.c"


class Record(ctypes.Structure):
    _fields_ = [
        ("output_x", ctypes.c_uint16),
        ("output_y", ctypes.c_uint16),
        ("packet_1", ctypes.c_uint32),
        ("packet_2", ctypes.c_uint32),
        ("packet_3", ctypes.c_uint32),
        ("packet_4", ctypes.c_uint32),
    ]


READ = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.c_void_p)
WRITE = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_uint32)


def bits(value):
    return struct.unpack("<I", struct.pack("<f", value))[0]


def main():
    with tempfile.TemporaryDirectory() as directory:
        library = pathlib.Path(directory) / "coordinate.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)],
            check=True,
        )
        dll = ctypes.CDLL(str(library))
        submit = dll.recovered_geometry_coordinate_submit
        submit.restype = ctypes.c_uint32
        submit.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint16),
            ctypes.POINTER(ctypes.c_uint16),
            ctypes.POINTER(Record),
            READ,
            WRITE,
            ctypes.c_void_p,
        ]

        table = (Record * 4)()
        table[2] = Record(0x1234, 0x5678, 0x11111111, 0x81234567, 0x33333333, 0x44444444)
        writes = []

        @READ
        def read(_):
            return 2 if len(writes) == 2 else 0xdeadbeef

        @WRITE
        def write(_, value):
            writes.append(value)

        out_x = ctypes.c_uint16()
        out_y = ctypes.c_uint16()
        result = submit(
            bits(513.75), bits(1023.9), ctypes.byref(out_x), ctypes.byref(out_y),
            table, read, write, None,
        )
        assert writes == [
            0x41, (511 << 9) + 256, 53, 0x11111111, bits(513.75),
            0x33333333, bits(1023.9), 0x44444444, 0x44444444, 0x01234567,
        ]
        assert (out_x.value, out_y.value) == (0x1234, 0x5678)
        assert result == 0xDEADBEEF

        writes.clear()
        assert submit(bits(-1.0), bits(1.0), ctypes.byref(out_x), ctypes.byref(out_y), table, read, write, None) == 0x47C34F80
        assert writes == []
        assert submit(bits(1024.0), bits(1.0), ctypes.byref(out_x), ctypes.byref(out_y), table, read, write, None) == 0x47C34F80
        assert writes == []

    print("recovered geometry coordinate vectors: ok")


if __name__ == "__main__":
    main()
