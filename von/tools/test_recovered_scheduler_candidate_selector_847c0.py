#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_candidate_selector_847c0.c"


class Selection(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "selected_result", "selected_index", "last_fifo_result",
        "fifo_packets", "early_zero_gate")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "candidate-selector.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library),
                    str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_scheduler_candidate_selector_847c0
    array_type = ctypes.c_int32 * 32
    words = ctypes.c_uint32 * 32
    build.argtypes = [ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32,
                      ctypes.c_int32, ctypes.c_int32, ctypes.c_uint32,
                      array_type, words, words, words]
    build.restype = Selection

    classifications = array_type(*([7] * 32))
    classifications[3] = 4
    classifications[7] = 2
    classifications[11] = 3
    responses = words(*range(32))
    zeros = words(*([0] * 32))
    result = build(0, 1, 0, 0, 0, 0, classifications, zeros, zeros, responses)
    assert (result.selected_result, result.selected_index,
            result.last_fifo_result, result.fifo_packets,
            result.early_zero_gate) == (2, 7, 7, 2, 0)

    result = build(1, 1, 0, 0, 0, 0, classifications, zeros, zeros, responses)
    assert (result.selected_result, result.selected_index,
            result.fifo_packets, result.early_zero_gate) == (2, 7, 2, 0)

    result = build(2, 1, 0, 0, 0, 0, classifications, zeros, zeros, responses)
    assert (result.selected_result, result.selected_index,
            result.last_fifo_result, result.fifo_packets,
            result.early_zero_gate) == (0, 0xffffffff, 0, 0, 1)

    result = build(0, 0, 0, 0, 0, 0, classifications, zeros, zeros, responses)
    assert result.early_zero_gate == 1 and result.selected_result == 0
    result = build(0, 6, 1 << 5, 14, 6, 1, classifications, zeros, zeros, responses)
    assert result.early_zero_gate == 1 and result.selected_result == 0
    result = build(0, 6, 1 << 5, 14, 5, 1, classifications, zeros, zeros, responses)
    assert result.early_zero_gate == 0 and result.selected_result == 2

    result = build(13, 1, 0, 0, 0, 0, classifications, zeros, zeros, responses)
    assert result.early_zero_gate == 1 and result.selected_result == 0
    result = build(14, 1, 0, 0, 0, 0, classifications, zeros, zeros, responses)
    assert (result.early_zero_gate, result.selected_result,
            result.selected_index) == (0, 2, 7)

    only_five = array_type(*([7] * 32))
    only_five[4] = 5
    result = build(14, 1, 0, 0, 0, 0, only_five, zeros, zeros, responses)
    assert (result.selected_result, result.selected_index,
            result.fifo_packets) == (5, 4, 1)

print("recovered 0x847c0 candidate-selector vectors: ok")

listing = [" ".join(line.split()) for line in
           (ROOT / "von/build/disasm/vonj-maincpu.lst").read_text(encoding="utf-8").splitlines()]
for address, instruction in (
        ("847d8:", "setbit 16,0,g3"),
        ("847e0:", "cmpi g3,g4"),
        ("847e8:", "bge 0x84800"),
        ("847ec:", "ldos 0x172(g0),g4"),
        ("847fc:", "cmpible g4,g3,0x84840"),
        ("84840:", "mov 0,r7"),
        ("84800:", "ld 0x64(g0),g4"),
        ("84818:", "bbc 5,g4,0x84848"),
        ("84820:", "cmpibe 1,g4,0x84834"),
        ("84828:", "cmpibne 14,g4,0x84848"),
        ("84830:", "cmpibne 6,g4,0x84848"),
        ("8483c:", "cmpibne 1,g4,0x84848"),
        ("84858:", "cmpibl 5,g0,0x848b0"),
        ("8485c:", "cmpibge g0,r7,0x848b0")):
    assert any(address in line and instruction in line for line in listing)

print("recovered 0x847c0 candidate-selector listing evidence: ok")
