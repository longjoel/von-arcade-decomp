#!/usr/bin/env python3
"""Check the selected-record packet prologue at i960 0x7d7f4."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_selected_packet_builder_7d7f4.c"


class Plan(ctypes.Structure):
    _fields_ = [
        ("table_base", ctypes.c_uint32),
        ("record_stride", ctypes.c_uint32),
        ("selected_index", ctypes.c_uint32),
        ("record_offset", ctypes.c_uint32),
        ("first_field_offset", ctypes.c_uint32),
        ("metric_field_offset", ctypes.c_uint32),
        ("enabled_field_offset", ctypes.c_uint32),
        ("command_count", ctypes.c_uint32),
        ("command_ids", ctypes.c_uint32 * 3),
        ("fifo_target", ctypes.c_uint32),
        ("classifier_target", ctypes.c_uint32),
        ("result_table_base", ctypes.c_uint32),
        ("result_destination", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-selected-packet.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_selected_packet_builder_7d7f4
    function.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]
    function.restype = None

    for index in (0, 3, 6):
        plan = Plan()
        function(index, ctypes.byref(plan))
        assert plan.table_base == 0x505060
        assert plan.record_stride == 6
        assert plan.record_offset == index * 6
        assert (plan.first_field_offset, plan.metric_field_offset,
                plan.enabled_field_offset) == (0, 2, 4)
        assert list(plan.command_ids) == [10, 29, 30]
        assert (plan.fifo_target, plan.classifier_target,
                plan.result_table_base, plan.result_destination) == (
                    0x884000, 0x73508, 0x72630, 0x504D94)

print("PASS: 0x7d7f4 selected-packet prologue vectors")
