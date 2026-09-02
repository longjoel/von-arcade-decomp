#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile


class Update(ctypes.Structure):
    _fields_ = [("target_kind", ctypes.c_uint32),
                ("target_slot", ctypes.c_uint32),
                ("target_offset", ctypes.c_uint32),
                ("value", ctypes.c_uint32)]


root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_link_release.c"
with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "link-release.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(source)], check=True)
    lib = ctypes.CDLL(str(library))
    function = lib.recovered_geometry_link_release_plan
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.POINTER(Update),
                         ctypes.POINTER(ctypes.c_uint32)]
    for link14 in (0, 3, 998, 999, 1000):
        for link18 in (1, 17, 999):
            updates = (Update * 2)()
            new_count = ctypes.c_uint32()
            function(7, link14, link18, 0, updates, ctypes.byref(new_count))
            if link14 == 999:
                assert (updates[0].target_kind, updates[0].target_slot,
                        updates[0].target_offset) == (0, 7, 0x5c8)
            else:
                assert (updates[0].target_kind, updates[0].target_slot,
                        updates[0].target_offset) == (1, link14, 0x18)
            assert updates[0].value == link18
            if link18 == 999:
                assert (updates[1].target_kind, updates[1].target_slot,
                        updates[1].target_offset) == (0, 7, 0x5c4)
            else:
                assert (updates[1].target_kind, updates[1].target_slot,
                        updates[1].target_offset) == (1, link18, 0x14)
            assert updates[1].value == link14
            assert new_count.value == 0xffffffff

print("recovered geometry link-release vectors: ok")
