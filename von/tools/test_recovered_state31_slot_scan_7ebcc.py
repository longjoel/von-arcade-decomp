#!/usr/bin/env python3
"""Check the active-slot scan and state-8 tail at i960 0x7ebcc."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state31_slot_scan_7ebcc.c"


class Plan(ctypes.Structure):
    _fields_ = [("candidate_count", ctypes.c_uint32),
                ("best_found", ctypes.c_uint32),
                ("best_index", ctypes.c_uint32),
                ("best_response", ctypes.c_uint32),
                ("best_mask", ctypes.c_uint32),
                ("packet_command", ctypes.c_uint32),
                ("packet_words", ctypes.c_uint32 * 4),
                ("state8_tail", ctypes.c_uint32),
                ("tail_control", ctypes.c_uint32),
                ("tail_selector", ctypes.c_uint32),
                ("tail_action", ctypes.c_uint32),
                ("tail_table_index", ctypes.c_uint32),
                ("tail_result", ctypes.c_uint32),
                ("tail_result_table", ctypes.c_uint32),
                ("tail_call_target", ctypes.c_uint32),
                ("scan_target", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate31-slot-scan.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state31_slot_scan_7ebcc
    array32 = ctypes.c_uint8 * 32
    word_array32 = ctypes.c_uint32 * 32
    function.argtypes = [array32, array32, word_array32, word_array32,
                         word_array32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.POINTER(Plan)]
    function.restype = None

    active = array32()
    below = array32()
    related_minus_8 = word_array32()
    related_0 = word_array32()
    responses = word_array32()
    active[2], active[7] = 0x12, 0x34
    below[2], below[7] = 1, 1
    related_minus_8[7], related_0[7], responses[7] = 0xaa, 0xbb, 0xcc
    plan = Plan()
    function(active, below, related_minus_8, related_0, responses,
             0x100, 0x200, 8, 0x55, 0x1234, ctypes.byref(plan))
    assert (plan.candidate_count, plan.best_found, plan.best_index,
            plan.best_response, plan.best_mask) == (2, 1, 7, 0xcc, 0x34)
    assert (plan.packet_command, list(plan.packet_words)) == (
        62, [0xaa, 0x100, 0xbb, 0x200])
    assert (plan.state8_tail, plan.tail_control, plan.tail_selector,
            plan.tail_table_index, plan.tail_result, plan.tail_result_table,
            plan.tail_call_target) == (1, 3, 0x64, 0x55, 0x1234,
                                       0x72780, 0x79050)

    below[7] = 0
    plan = Plan()
    function(active, below, related_minus_8, related_0, responses,
             0, 0, 7, 0, 0, ctypes.byref(plan))
    assert (plan.best_found, plan.best_response) == (1, 0)
    assert plan.state8_tail == 0

print("recovered 0x7ebcc slot-scan vectors: ok")
