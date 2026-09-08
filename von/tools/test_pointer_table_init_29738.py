#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_pointer_table_init_29738.c"


class ServicePlan(ctypes.Structure):
    _fields_ = [
        ("store_address", ctypes.c_uint32 * 6),
        ("store_value", ctypes.c_uint32 * 6),
        ("store_count", ctypes.c_uint32),
        ("first_helper", ctypes.c_uint32),
        ("first_head", ctypes.c_uint32),
        ("first_stride", ctypes.c_uint32),
        ("second_helper", ctypes.c_uint32),
        ("second_head", ctypes.c_uint32),
        ("second_stride", ctypes.c_uint32),
    ]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "pointer-table.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    service = lib.recovered_pointer_service_init_plan
    service.argtypes = [ctypes.POINTER(ServicePlan)]
    setup = ServicePlan()
    service(ctypes.byref(setup))
    assert setup.store_count == 6
    assert list(setup.store_address) == [0x515098, 0x51509c, 0x5150a8,
                                         0x5150ac, 0x5150b0, 0x5150b4]
    assert list(setup.store_value) == [0, 0, 0x515090, 0, 0x5150c0, 0x5190c0]
    assert (setup.first_helper, setup.first_head, setup.first_stride,
            setup.second_helper, setup.second_head, setup.second_stride) == (
        0x29778, 0x5150c0, 0x100, 0x29738, 0x5190c0, 0x40)
    fn = lib.recovered_pointer_table_init_29738
    fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
    for head, stride in ((0x5150C0, 0x40), (0x5190C0, 0x100)):
        links = (ctypes.c_uint32 * 64)(*[0xffffffff] * 64)
        fn(head, stride, links)
        assert links[0] == head + stride
        assert links[62] == head + 63 * stride
        assert links[63] == 0

print("PASS: original 0x29738/0x29778 pointer-table initialization")
