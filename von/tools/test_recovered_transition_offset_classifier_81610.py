#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_offset_classifier_81610.c"
RUNTIME_MATH = ROOT / "von/i960/recovered_runtime_math.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "object_pointer", "object_value_74", "classifier_input_g2",
        "timing_low_g0", "timing_high_g1", "global_state_504d70",
        "signed_g2_minus_3", "status_tail_target", "classifier_input",
        "classifier_bias", "classifier_target", "classifier_index",
        "result_table", "result_value", "action_destination", "action_value",
        "result_destination", "result_status", "helper_target", "tail_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "offset-classifier.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE), str(RUNTIME_MATH)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_transition_offset_classifier_81610
    build.argtypes = [ctypes.c_uint32] * 7 + [ctypes.POINTER(Plan)]

    plan = Plan()
    build(0x1000, 7, 6, 0xaaaa, 0x12345678, 3, 0x2222, ctypes.byref(plan))
    assert (plan.signed_g2_minus_3, plan.classifier_input,
            plan.classifier_bias, plan.tail_target) == (3, 0x1678, 0xffffc000, 0x79050)
    assert (plan.classifier_index, plan.result_table, plan.action_destination,
            plan.action_value, plan.helper_target) == (2, 0x72780, 0x504DB8, 30, 0x79050)

    build(0x2000, 8, 6, 0xbbbb, 0x00001234, 4, 0x3333, ctypes.byref(plan))
    assert (plan.signed_g2_minus_3, plan.classifier_input,
            plan.classifier_bias, plan.tail_target) == (3, 0xffffd234, 0xffffc000, 0x79050)

    build(0x2500, 8, 6, 0xbbbb, 0x00001234, 5, 0x3333, ctypes.byref(plan))
    assert (plan.classifier_input, plan.classifier_bias) == (0x5234, 0x4000)

    build(0x2800, 8, 6, 0xbbbb, 0x00008000, 5, 0x3333, ctypes.byref(plan))
    assert plan.classifier_input == 0xffffc000

    build(0x3000, 9, 5, 0xcccc, 0x00001234, 2, 0x4444, ctypes.byref(plan))
    assert (plan.signed_g2_minus_3, plan.tail_target) == (2, 0x8168C)

    build(0x4000, 10, 2, 0xdddd, 0x00001234, 2, 0x5555, ctypes.byref(plan))
    assert (plan.signed_g2_minus_3, plan.tail_target) == (0xffffffff, 0x8168C)


listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, text in (
    ("81620", "subo 3,g2,g4"),
    ("81624", "cmpo 3,g4"),
    ("81634", "cmpibl 4,g4,0x81650"),
    ("81638", "shlo 16,g1,g0"),
    ("81640", "lda 0xffffc000(g0),g0"),
    ("81648", "bal 0x73508"),
    ("81650", "shlo 16,g1,g0"),
    ("81658", "lda 0x4000(g0),g0"),
    ("81660", "bal 0x73508"),
    ("81664", "ld 0x72780[g0*4],g4"),
):
    normalized_text = " ".join(text.split())
    assert any(address + ":" in line and normalized_text in line for line in listing), \
        f"81610 listing dataflow missing: {address} {text}"

print("recovered 0x81610 offset-classifier vectors: ok")
