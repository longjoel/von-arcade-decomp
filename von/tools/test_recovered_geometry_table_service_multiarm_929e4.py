#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_table_service_multiarm_929e4.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("929e4", "ld"), ("929ec", "shlo"),
                      ("929f0", "lda"), ("929f8", "cmpobg"),
                      ("92b20", "lda"), ("92b28", "cmpobg"),
                      ("92c50", "lda"), ("92c58", "cmpobg"),
                      ("92d84", "mov"), ("92da0", "ld")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "source_value", "threshold_value", "guard_value_0", "guard_value_1",
        "guard_value_2", "arm_target_0", "arm_target_1", "arm_target_2",
        "adjusted_packet_source_0", "adjusted_packet_source_1",
        "adjusted_packet_source_2", "operand_word_0", "operand_word_1",
        "operand_word_2", "selected_arm", "selected_source", "selected_operand",
        "completion_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "dispatcher.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_table_service_multiarm_929e4
    function.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]
    plan = Plan()
    function(100, ctypes.byref(plan))
    assert (plan.threshold_value, plan.guard_value_0, plan.guard_value_1,
            plan.guard_value_2, plan.selected_arm, plan.selected_source,
            plan.selected_operand) == (120, 40, 30, 20, 0, 100, 0xb800)
    function(185, ctypes.byref(plan))
    assert (plan.selected_arm, plan.selected_source, plan.selected_operand) == (1, 175, 0xc000)
    function(200, ctypes.byref(plan))
    assert (plan.selected_arm, plan.selected_source, plan.selected_operand) == (2, 180, 0xc800)
    function(261, ctypes.byref(plan))
    assert plan.selected_arm == 3

print("recovered geometry 0x929e4 multiarm-dispatch fixture: ok")
