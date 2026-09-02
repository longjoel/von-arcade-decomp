#!/usr/bin/env python3
"""Validate the packet and output contract of the 0x9e450 builder."""

from __future__ import annotations

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_result_builder_9e450.c"
MAINCPU = ROOT / "von/build/disasm/vonj-maincpu.lst"

maincpu = MAINCPU.read_text(encoding="utf-8")
for address in ("a0b08", "a70e8", "b2428"):
    line = next((line for line in maincpu.splitlines() if f"{address}:" in line), "")
    if "lda\t0x58(g2),r6" not in line:
        raise SystemExit(f"0x9e450 caller seed missing at {address}")

for address in ("a0bb4", "a7134", "b2474"):
    line = next((line for line in maincpu.splitlines() if f"{address}:" in line), "")
    if "addo\tr6,g2,g2" not in line:
        raise SystemExit(f"0x9e450 caller record-base addition missing at {address}")


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
        ("flag_set_delta_command_base", ctypes.c_uint32),
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

class Followups(ctypes.Structure):
    _fields_ = [
        ("command29", ctypes.c_uint32 * 3),
        ("command30", ctypes.c_uint32 * 3),
        ("output_18", ctypes.c_uint32),
        ("output_20", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory(prefix="von-result-builder-9e450-") as directory:
    library = pathlib.Path(directory) / "builder.so"
    subprocess.run(
        ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)],
        check=True,
    )
    function = ctypes.CDLL(str(library)).recovered_geometry_result_builder_9e450_plan
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
    function.restype = None

    clear = Plan()
    function(2, 0, ctypes.byref(clear))
    assert clear.selector == 2
    assert clear.selector_stride_bytes == 12
    assert clear.flag_set_delta_command_base == 0
    assert clear.flag_clear_source_offset == 0x184
    assert clear.common_request31_word_count == 7

    flagged = Plan()
    function(7, 1, ctypes.byref(flagged))
    assert (flagged.flag_set_delta_command_base, flagged.flag_set_delta_word_count) == (31, 4)
    assert flagged.flag_set_delta_response_output_offset == 0x0E
    assert flagged.final_response_offset == 0x28
    assert (flagged.followup_command29, flagged.followup_command29_word_count) == (29, 3)
    assert flagged.followup_command29_response_output_offset == 0x18
    assert flagged.followup_command29_response_transform == 0x80000000
    assert (flagged.followup_command30, flagged.followup_command30_word_count) == (30, 3)
    assert flagged.followup_command30_response_output_offset == 0x20
    assert flagged.followup_command30_table_base == 0x562CB0
    assert list(flagged.followup_table_output_offset) == [0x14, 0x24]

transform = ctypes.CDLL(str(library)).recovered_geometry_result_builder_command29_response
transform.argtypes = [ctypes.c_uint32]
transform.restype = ctypes.c_uint32
assert transform(0x01234567) == 0x81234567
assert transform(0x81234567) == 0x01234567

followups_fn = ctypes.CDLL(str(library)).recovered_geometry_result_builder_followups
followups_fn.argtypes = [
    ctypes.c_int16, ctypes.c_uint32, ctypes.c_uint32,
    ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Followups),
]
followups = Followups()
followups_fn(-2, 0x11111111, 0x22222222, 0x01234567, 0x89abcdef,
             ctypes.byref(followups))
assert list(followups.command29) == [29, 0xfffffffe, 0x11111111]
assert list(followups.command30) == [30, 0xfffe, 0x22222222]
assert (followups.output_18, followups.output_20) == (0x81234567, 0x89abcdef)

delta_fn = ctypes.CDLL(str(library)).recovered_geometry_result_builder_flag_set_delta_packet
delta_fn.argtypes = [
    ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
    ctypes.POINTER(ctypes.c_uint32),
]
delta_fn.restype = None
linked = (ctypes.c_uint32 * 3)(100, 200, 300)
responses = (ctypes.c_uint32 * 3)(7, 11, 13)
packet = (ctypes.c_uint32 * 4)()
delta_fn(linked, responses, packet)
assert list(packet) == [124, 93, 189, 287]

wrapped_linked = (ctypes.c_uint32 * 3)(0, 0, 0)
wrapped_responses = (ctypes.c_uint32 * 3)(1, 2, 3)
delta_fn(wrapped_linked, wrapped_responses, packet)
assert list(packet) == [30, 0xffffffff, 0xfffffffe, 0xfffffffd]

table_address = ctypes.CDLL(str(library)).recovered_geometry_result_builder_followup_table_address
table_address.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
table_address.restype = ctypes.c_uint32
assert table_address(3, 0) == 0x562cb0 + 3 * 3 * 16
assert table_address(0x103, 0x14) == 0x562cb0 + 3 * 3 * 16 + 0x14

print("PASS: 0x9e450 result-builder contract")
