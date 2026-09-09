#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_first_continuation_handoff_8e110.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address in ("8e110", "8e114", "8e118", "8e11c"):
    assert any(address + ":" in line and "addo" in line for line in listing.splitlines())


class Input(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "table_cursor", "auxiliary_cursor", "source_cursor", "destination_cursor")]


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "next_table_cursor", "next_auxiliary_cursor", "next_source_cursor",
        "next_destination_cursor", "continuation_entry")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "handoff.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_first_continuation_handoff_8e110
    function.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    sample = Input(0x1000, 0x2000, 0x3000, 0x4000)
    plan = Plan()
    function(ctypes.byref(sample), ctypes.byref(plan))
    assert (plan.next_table_cursor, plan.next_auxiliary_cursor,
            plan.next_source_cursor, plan.next_destination_cursor,
            plan.continuation_entry) == (0x100c, 0x2002, 0x3008, 0x4008, 0x8e120)

print("recovered geometry 0x8e110 continuation handoff fixture: ok")
