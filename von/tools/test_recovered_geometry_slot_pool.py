#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_slot_pool.c"
with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "slot-pool.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(source)], check=True)
    lib = ctypes.CDLL(str(library))
    for width, acquire_name, release_name in ((64, "recovered_geometry_pool64_acquire", "recovered_geometry_pool64_release"),
                                               (32, "recovered_geometry_pool32_acquire", "recovered_geometry_pool32_release")):
        slots = (ctypes.c_uint32 * (width + 1))(*range(width + 1))
        acquire = getattr(lib, acquire_name)
        acquire.restype = ctypes.c_uint32
        acquire.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
        for count in range(width + 2):
            new_count = ctypes.c_uint32()
            value = acquire(slots, count, ctypes.byref(new_count))
            if count < width:
                assert new_count.value == count + 1 and value == count + 1
            else:
                assert new_count.value == count and value == 0xffffffff

        release = getattr(lib, release_name)
        release.restype = ctypes.c_uint32
        release.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
        for count in range(1, width + 1):
            new_count = ctypes.c_uint32()
            assert release(slots, count, 0xa5000000 | count, ctypes.byref(new_count)) == 1
            assert new_count.value == count - 1
            assert slots[count - 1] == 0xa5000000 | count

    reset = lib.recovered_geometry_pool32_reset
    reset.restype = None
    reset.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
    slots = (ctypes.c_uint32 * 32)(*[0xfeed0000 + index for index in range(32)])
    count = ctypes.c_uint32(31)
    reset(slots, ctypes.byref(count))
    assert count.value == 0
    assert list(slots) == [0] * 32

    reset64 = lib.recovered_geometry_pool64_reset
    reset64.restype = None
    reset64.argtypes = [ctypes.POINTER(ctypes.c_uint32),
                        ctypes.POINTER(ctypes.c_uint32),
                        ctypes.POINTER(ctypes.c_uint32)]
    slots64 = (ctypes.c_uint32 * 64)(*[0xbeef0000 + index for index in range(64)])
    fields64 = (ctypes.c_uint32 * 64)(*[0xcafe0000 + index for index in range(64)])
    count64 = ctypes.c_uint32(63)
    reset64(slots64, fields64, ctypes.byref(count64))
    assert count64.value == 0
    assert list(slots64) == [0] * 64
    assert list(fields64) == [0] * 64

print("recovered geometry slot-pool vectors: ok")
