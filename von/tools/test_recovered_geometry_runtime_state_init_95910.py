#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_runtime_state_init_95910.c"

class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "seed_table_address", "seed_word", "seed_record_count",
        "clear_table_address", "clear_record_count",
        "global_5624ac_address", "global_5624ac_value",
        "global_5624b8_address", "global_5624b8_value",
        "global_5624c4_address", "global_5624c4_value")]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "runtime-init.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_geometry_runtime_state_init_95910
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.POINTER((ctypes.c_uint32 * 3)),
                         ctypes.POINTER((ctypes.c_uint32 * 3)), ctypes.POINTER(Plan)]
    seeded = ((ctypes.c_uint32 * 3) * 3)(*[((1, 2, 3)) for _ in range(3)])
    cleared = ((ctypes.c_uint32 * 3) * 4)(*[(4, 5, 6) for _ in range(4)])
    plan = Plan()
    function(0xdeadbeef, 9, 3, seeded, cleared, ctypes.byref(plan))
    assert [list(seeded[i]) for i in range(3)] == [[0xdeadbeef] * 3] * 3
    assert [list(cleared[i]) for i in range(4)] == [[0, 0, 0]] * 4
    assert (plan.seed_table_address, plan.seed_word, plan.seed_record_count,
            plan.clear_table_address, plan.clear_record_count) == \
           (0x562490, 0xdeadbeef, 3, 0x562500, 4)
    assert (plan.global_5624ac_address, plan.global_5624ac_value,
            plan.global_5624b8_address, plan.global_5624b8_value,
            plan.global_5624c4_address, plan.global_5624c4_value) == \
           (0x5624ac, 40, 0x5624b8, 0xb4, 0x5624c4, 0xfa)
print("recovered geometry 0x95910 runtime-state initializer: ok")
