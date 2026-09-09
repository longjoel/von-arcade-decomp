#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_candidate_packet_81b30.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("81bc0", "st"), ("81bd0", "st"),
                      ("81be8", "addo"), ("81bf4", "st"),
                      ("81c0c", "st"), ("81c14", "st"),
                      ("81c80", "cmpibne"), ("81c98", "ldis"),
                      ("81cfc", "mov"), ("81d10", "and"),
                      ("81d14", "st"), ("81d88", "ld"),
                      ("81d98", "subr"), ("81ddc", "bal"),
                      ("81de4", "cmpibe"), ("81e10", "ld"),
                      ("81e20", "st"), ("81e34", "ld"),
                      ("81e5c", "ret")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())

class Input(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "candidate_cell0_integer", "candidate_cell2_integer", "related_plus8",
        "related_plus10")]

class Plan(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32 * 8), ("fifo_count", ctypes.c_uint32)]

class Selection(ctypes.Structure):
    _fields_ = [("candidate_present", ctypes.c_uint32),
                ("selected_cell_offset", ctypes.c_uint32)]

class Cursor(ctypes.Structure):
    _fields_ = [("candidate_valid", ctypes.c_uint32),
                ("candidate_count", ctypes.c_uint32),
                ("cell_offset", ctypes.c_uint32),
                ("field_offset", ctypes.c_uint32 * 3)]

class Followup(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32 * 6), ("fifo_count", ctypes.c_uint32)]

class ResponseTail(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32 * 14), ("fifo_count", ctypes.c_uint32)]

class ClassifierPrefix(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32 * 3), ("fifo_count", ctypes.c_uint32),
                ("classifier_input", ctypes.c_uint32),
                ("classifier_target", ctypes.c_uint32)]

class ClassifierPublication(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "result_table", "result_value", "action_destination", "action_value",
        "result_destination", "result_status", "phase_destination",
        "phase_value", "return_value")]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "candidate.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    fn = ctypes.CDLL(str(library)).recovered_geometry_candidate_packet_81b30
    fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    sample = Input(100, 250, 7, 11)
    plan = Plan()
    fn(ctypes.byref(sample), ctypes.byref(plan))
    assert list(plan.fifo_word) == [10, 239, 0xffffffa3, 62, 100, 100, 250, 11]
    assert plan.fifo_count == 8
    wrapped = Input(0, 1, 2, 3)
    fn(ctypes.byref(wrapped), ctypes.byref(plan))
    assert list(plan.fifo_word) == [10, 0xfffffffe, 2, 62, 0, 0, 1, 3]
    select = ctypes.CDLL(str(library)).recovered_geometry_candidate_selection_81b30
    select.argtypes = [ctypes.c_uint32, ctypes.POINTER(Selection)]
    selection = Selection()
    select(0xffffffff, ctypes.byref(selection))
    assert (selection.candidate_present, selection.selected_cell_offset) == (0, 0xfffffffa)
    select(6, ctypes.byref(selection))
    assert (selection.candidate_present, selection.selected_cell_offset) == (1, 36)
    cursor_fn = ctypes.CDLL(str(library)).recovered_geometry_candidate_scan_cursor_81b30
    cursor_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Cursor)]
    cursor = Cursor()
    cursor_fn(6, ctypes.byref(cursor))
    assert (cursor.candidate_valid, cursor.candidate_count, cursor.cell_offset) == (1, 7, 36)
    assert tuple(cursor.field_offset) == (0, 2, 4)
    cursor_fn(7, ctypes.byref(cursor))
    assert cursor.candidate_valid == 0 and cursor.candidate_count == 7
    followup_fn = ctypes.CDLL(str(library)).recovered_geometry_followup_packet_81b30
    followup_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.POINTER(Followup)]
    followup = Followup()
    followup_fn(100, 250, 300, 7, 11, 0x1234abcd, ctypes.byref(followup))
    assert list(followup.fifo_word) == [10, 239, 0xffffffa3, 29, 0xabcd, 300]
    assert followup.fifo_count == 6
    tail_fn = ctypes.CDLL(str(library)).recovered_geometry_response_tail_81b30
    tail_fn.argtypes = [ctypes.c_uint32] * 8 + [ctypes.POINTER(ResponseTail)]
    tail = ResponseTail()
    tail_fn(100, 250, 300, 7, 11, 0x1234abcd, 500, 600, ctypes.byref(tail))
    assert list(tail.fifo_word) == [10, 239, 0xffffffa3, 29, 0xabcd, 300,
                                    30, 0xffffffa3, 300, 62, 0xfffffe70, 7, 850, 11]
    assert tail.fifo_count == 14
    prefix_fn = ctypes.CDLL(str(library)).recovered_geometry_classifier_prefix_81d88
    prefix_fn.argtypes = [ctypes.c_uint32] * 6 + [ctypes.POINTER(ClassifierPrefix)]
    prefix = ClassifierPrefix()
    prefix_fn(100, 250, 7, 11, 0x1234abcd, 0xfff0, ctypes.byref(prefix))
    assert list(prefix.fifo_word) == [10, 239, 0xffffffa3]
    assert prefix.fifo_count == 3
    assert prefix.classifier_input == 0xffffabdd
    assert prefix.classifier_target == 0x73508
    publish_fn = ctypes.CDLL(str(library)).recovered_geometry_classifier_publication_81de0
    publish_fn.argtypes = [ctypes.c_uint32] * 5 + [ctypes.POINTER(ClassifierPublication)]
    publication = ClassifierPublication()
    publish_fn(2, 1, 0x1234, 0x5678, 9, ctypes.byref(publication))
    assert (publication.result_table, publication.result_value,
            publication.action_value, publication.result_destination,
            publication.phase_value, publication.return_value) == (
                0x72780, 0x1234, 30, 0x504d94, 9, 1)
    publish_fn(7, 0, 0x1234, 0x5678, 10, ctypes.byref(publication))
    assert (publication.result_table, publication.result_value,
            publication.action_value) == (0x72630, 0x5678, 5)
    publish_fn(3, 1, 0x1234, 0x5678, 11, ctypes.byref(publication))
    assert (publication.result_table, publication.action_value) == (0x72630, 5)
print("recovered geometry 0x81b30 candidate packet: ok")
