#!/usr/bin/env python3
"""Validate the distinct flag branches of the 0x9e250 result builder."""

from __future__ import annotations

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_result_builder_9e250.c"


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
        ("flag_set_delta_request", ctypes.c_uint32),
        ("flag_set_compare_uses_signed_paired_halfword", ctypes.c_uint32),
        ("flag_set_alternate_table", ctypes.c_uint32),
        ("flag_clear_constant", ctypes.c_uint32),
        ("flag_clear_writes_output_offset", ctypes.c_uint32),
        ("common_request31", ctypes.c_uint32),
        ("common_request31_word_count", ctypes.c_uint32),
        ("final_sharc_handler", ctypes.c_uint32),
        ("final_host_read_pc", ctypes.c_uint32),
        ("final_response_offset", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory(prefix="von-result-builder-9e250-") as directory:
    library = pathlib.Path(directory) / "builder.so"
    subprocess.run(
        ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)],
        check=True,
    )
    function = ctypes.CDLL(str(library)).recovered_geometry_result_builder_9e250_plan
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
    function.restype = None

    clear = Plan()
    function(3, 0, ctypes.byref(clear))
    assert clear.selector == 3
    assert clear.selector_stride_bytes == 12
    assert clear.flag_set_delta_request == 0
    assert clear.flag_clear_constant == 0xffffe000
    assert clear.flag_clear_writes_output_offset == 0x0C

    flagged = Plan()
    function(7, 1, ctypes.byref(flagged))
    assert flagged.flag_set_delta_request == 1
    assert flagged.flag_set_compare_uses_signed_paired_halfword == 1
    assert flagged.flag_set_alternate_table == 0x562CB0
    assert flagged.common_request31 == 31
    assert flagged.common_request31_word_count == 7
    assert flagged.final_sharc_handler == 0x203EA
    assert flagged.final_host_read_pc == 0x9E438
    assert flagged.final_response_offset == 0x28

print("PASS: 0x9e250 result-builder variant")
