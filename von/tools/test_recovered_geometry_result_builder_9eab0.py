#!/usr/bin/env python3
"""Validate the default-initialized sibling of the 0x9e880 result builder."""

from __future__ import annotations

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_result_builder_9eab0.c"


class Plan(ctypes.Structure):
    _fields_ = [
        ("selector", ctypes.c_uint32),
        ("selector_stride_bytes", ctypes.c_uint32),
        ("parameter_table_address", ctypes.c_uint32),
        ("request38_address", ctypes.c_uint32),
        ("request38_word_count", ctypes.c_uint32),
        ("response_scratch_offset", ctypes.c_uint32),
        ("paired_record_offset", ctypes.c_uint32 * 3),
        ("paired_record_mirror_offset", ctypes.c_uint32 * 3),
        ("flag_offset", ctypes.c_uint32),
        ("initial_default_value", ctypes.c_uint32),
        ("initial_default_output_offset", ctypes.c_uint32),
        ("initial_default_paired_offset", ctypes.c_uint32),
        ("flag_set_delta_command", ctypes.c_uint32),
        ("flag_set_delta_word_count", ctypes.c_uint32),
        ("flag_set_delta_response_output_offset", ctypes.c_uint32),
        ("flag_clear_source_offset", ctypes.c_uint32),
        ("flag_clear_response_output_offset", ctypes.c_uint32),
        ("common_request31", ctypes.c_uint32),
        ("common_request31_word_count", ctypes.c_uint32),
        ("final_response_offset", ctypes.c_uint32),
        ("followup_command29", ctypes.c_uint32),
        ("followup_command29_word_count", ctypes.c_uint32),
        ("followup_command29_response_output_offset", ctypes.c_uint32),
        ("followup_command29_response_transform", ctypes.c_uint32),
        ("followup_command30", ctypes.c_uint32),
        ("followup_command30_word_count", ctypes.c_uint32),
        ("followup_command30_response_output_offset", ctypes.c_uint32),
        ("followup_command30_table_base", ctypes.c_uint32),
        ("followup_table_output_offset", ctypes.c_uint32 * 2),
    ]


with tempfile.TemporaryDirectory(prefix="von-result-builder-9eab0-") as directory:
    library = pathlib.Path(directory) / "builder.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_result_builder_9eab0_plan
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
    function.restype = None

    clear = Plan()
    function(4, 0, ctypes.byref(clear))
    assert clear.selector == 4
    assert clear.initial_default_value == 0xffffe000
    assert (clear.initial_default_output_offset, clear.initial_default_paired_offset) == (0x0C, 0x06)
    assert clear.flag_set_delta_command == 0
    assert clear.flag_clear_source_offset == 0x184

    flagged = Plan()
    function(8, 1, ctypes.byref(flagged))
    assert (flagged.flag_set_delta_command, flagged.flag_set_delta_word_count) == (10, 3)
    assert flagged.followup_command29_response_transform == 0x80000000
    assert flagged.flag_set_delta_response_output_offset == 0x0E
    assert (flagged.followup_command29, flagged.followup_command29_word_count) == (29, 3)
    assert (flagged.followup_command30, flagged.followup_command30_word_count) == (30, 3)
    assert list(flagged.followup_table_output_offset) == [0x14, 0x24]

packet_fn = ctypes.CDLL(str(library)).recovered_geometry_result_builder_9eab0_flag_set_packet
packet_fn.argtypes = [
    ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
    ctypes.POINTER(ctypes.c_uint32),
]
packet_fn.restype = None
linked = (ctypes.c_uint32 * 3)(100, 200, 300)
responses = (ctypes.c_uint32 * 3)(7, 11, 13)
packet = (ctypes.c_uint32 * 3)()
packet_fn(linked, responses, packet)
assert list(packet) == [10, 287, 93]

print("PASS: 0x9eab0 result-builder contract")
