#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_command62_packet_80400.c"

class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "selected_word_10", "selected_word_18", "object_word_8",
        "object_word_10", "packet_opcode", "packet_payload_0",
        "packet_payload_1", "packet_payload_2", "packet_payload_3",
        "board_response", "packet_words", "fifo_destination",
        "floating_gate_start")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "command62-packet.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_geometry_command62_packet_80400
    build.argtypes = [
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]

    plan = Plan()
    build(0x11111111, 0x22222222, 0x33333333, 0x44444444,
          0xABCDEF01, ctypes.byref(plan))
    assert plan.packet_opcode == 62
    assert list((plan.packet_payload_0, plan.packet_payload_1,
                 plan.packet_payload_2, plan.packet_payload_3)) == [
        0x11111111, 0x33333333, 0x22222222, 0x44444444]
    assert plan.board_response == 0xABCDEF01
    assert plan.packet_words == 5
    assert plan.fifo_destination == 0x884000
    assert plan.floating_gate_start == 0x80428

print("recovered 0x80400 command-62 packet vectors: ok")
