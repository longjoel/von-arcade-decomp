#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_runtime_state_init_95984.c"

class Plan(ctypes.Structure):
    _fields_ = [("constant_address", ctypes.c_uint32), ("constant_value", ctypes.c_uint32),
                ("zero_doubleword_address", ctypes.c_uint32 * 2),
                ("status_table_address", ctypes.c_uint32), ("status_word", ctypes.c_uint32),
                ("status_word_count", ctypes.c_uint32), ("ready_word_address", ctypes.c_uint32),
                ("ready_word_value", ctypes.c_uint32), ("state_cluster_address", ctypes.c_uint32),
                ("state_cluster_word", ctypes.c_uint32 * 7)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "runtime-init-95984.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_geometry_runtime_state_init_95984
    function.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
                         ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(Plan)]
    status = (ctypes.c_uint32 * 6)(*[1] * 6)
    cluster = (ctypes.c_uint32 * 7)(*[1] * 7)
    plan = Plan()
    function(0x12345678, status, cluster, ctypes.byref(plan))
    assert list(status) == [0x12345678] * 6
    assert list(cluster) == [0x12345678, 0, 0, 0, 0x12345678, 0x12345678, 0x12345678]
    assert (plan.constant_address, plan.constant_value,
            list(plan.zero_doubleword_address), plan.status_table_address,
            plan.status_word_count, plan.ready_word_address,
            plan.ready_word_value, plan.state_cluster_address) == \
           (0x562538, 0xc059999a, [0x5624f0, 0x562530], 0x5624d0,
            6, 0x503aac, 0x12345678, 0x562b40)
print("recovered geometry 0x95984 runtime-state initializer: ok")
