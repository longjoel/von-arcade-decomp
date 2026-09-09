#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_transform_payload_select_df070.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("df0cc", "cmpibe"), ("df0d0", "cmpibl"),
                      ("df0f4", "ld"), ("df104", "ld"), ("df114", "mov")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())

class Input(ctypes.Structure):
    _fields_ = [("record_present", ctypes.c_uint32), ("record_class", ctypes.c_uint32),
                ("object_payload", ctypes.c_uint32 * 3),
                ("class_one_payload", ctypes.c_uint32 * 3),
                ("class_two_payload", ctypes.c_uint32 * 3)]

class Plan(ctypes.Structure):
    _fields_ = [("selected_payload", ctypes.c_uint32 * 3),
                ("selected_class", ctypes.c_uint32),
                ("payload_selected", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "payload.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    fn = ctypes.CDLL(str(library)).recovered_geometry_transform_payload_select_df070
    fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    sample = Input(1, 1, (10, 11, 12), (20, 21, 22), (30, 31, 32))
    for record_class, expected, selected in (
        (0, (10, 11, 12), 0), (1, (20, 21, 22), 1),
            (2, (30, 31, 32), 1), (3, (0, 0, 0), 0)):
        sample.record_class = record_class
        plan = Plan()
        fn(ctypes.byref(sample), ctypes.byref(plan))
        assert tuple(plan.selected_payload) == expected
        assert plan.selected_class == record_class
        assert plan.payload_selected == selected
    sample.record_present = 0
    plan = Plan()
    fn(ctypes.byref(sample), ctypes.byref(plan))
    assert tuple(plan.selected_payload) == (0, 0, 0)
print("recovered geometry 0xdf070 transform payload selector: ok")
