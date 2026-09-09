#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_command_prefix_7ff40.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "object_base", "selector", "object_table_base", "object_byte_address",
        "selected_object_byte", "reduced_profile", "profile_index",
        "profile_table_base",
        "profile_record_address", "profile_record_plus4", "profile_sum",
        "profile_scalar_bits", "profile_scalar_source", "profile_record_plus48",
        "profile_record_plus56", "initial_command", "fifo_destination")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "command-prefix.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_geometry_command_prefix_7ff40
    build.argtypes = [
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ctypes.c_uint32, ctypes.POINTER(Plan)]

    plan = Plan()
    build(0x10000000, 3, 0x20000000, 7, 0x562CB0,
          0x3F800000, 0x40000000, 0x40400000, 0x40800000,
          ctypes.byref(plan))
    assert plan.object_table_base == 0x20000200
    assert plan.object_byte_address == 0x20000260
    assert plan.selected_object_byte == 7
    assert plan.reduced_profile == 0
    assert plan.profile_index == 7
    assert plan.profile_record_address == 0x562CB0 + (7 * 48)
    assert plan.profile_sum == 0x7F800000
    assert plan.profile_scalar_bits == 0x41200000
    assert plan.profile_record_plus48 == 0x40400000
    assert plan.profile_record_plus56 == 0x40800000
    assert plan.initial_command == 30
    assert plan.fifo_destination == 0x884000

    build(0, 0, 0, 1, 0x562CB0, 1, 2, 3, 4, ctypes.byref(plan))
    assert plan.reduced_profile == 0
    assert plan.profile_index == 1
    build(0, 0, 0, 0, 0x562CB0, 1, 2, 3, 4, ctypes.byref(plan))
    assert plan.reduced_profile == 0xFFFFFFFF
    assert plan.profile_index == 0


listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, text in (
    ("7ff5c", "ldob (g5)[g12],g4"),
    ("7ff60", "mov g4,r8"),
    ("7ff68", "remi 6,g4,g4"),
    ("7ff74", "shlo 1,r8,g6"),
    ("7ff80", "addo g2,g6,g5"),
):
    normalized_text = " ".join(text.split())
    assert any(address + ":" in line and normalized_text in line for line in listing), \
        f"7ff40 listing dataflow missing: {address} {text}"

print("recovered 0x7ff40 geometry command prefix vectors: ok")
