#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_table_threshold_gates_92fc0.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("92fc0", "lda"), ("92fc8", "cmpobg"),
                      ("930f0", "lda"), ("930f8", "cmpobg")):
    assert any(address + ":" in line and text in line
               for line in listing.splitlines())


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "source_value", "threshold_value", "adjusted_value",
        "selected_target", "packet_target", "fallback_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "gates.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I",
                    str(root / "von/i960"), "-o", str(library),
                    str(source)], check=True)
    dll = ctypes.CDLL(str(library))
    for name, subtract_value, packet_target, fallback_target in (
        ("recovered_geometry_table_entry_gate_92fc0", 0x46, 0x92fcc, 0x930f0),
        ("recovered_geometry_table_entry_gate_930f0", 0x50, 0x930fc, 0x93224),
    ):
        function = getattr(dll, name)
        function.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                             ctypes.POINTER(Plan)]
        plan = Plan()
        function(0x5624b8, 120 + subtract_value, ctypes.byref(plan))
        assert (plan.threshold_value, plan.adjusted_value,
                plan.selected_target, plan.packet_target,
                plan.fallback_target) == (120, 120, packet_target,
                                           packet_target, fallback_target)
        function(0x5624b8, 121 + subtract_value, ctypes.byref(plan))
        assert (plan.adjusted_value, plan.selected_target) == (121, fallback_target)

print("recovered geometry 0x92fc0/0x930f0 threshold fixtures: ok")
