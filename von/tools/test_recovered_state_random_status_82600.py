#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_random_status_82600.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_int32 if name in ("random_value", "remainder_mod3") else ctypes.c_uint32) for name in (
        "random_value", "remainder_mod3", "writes_status",
        "status_504d80", "destination")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "random-status.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(SOURCE)], check=True)
    lib = ctypes.CDLL(str(library))
    build = lib.recovered_state_random_status_82600
    build.argtypes = [ctypes.c_int32]
    build.restype = Plan

    for value, status in ((0, 20), (1, 19), (2, 33), (3, 20)):
        result = build(value)
        assert (result.random_value, result.remainder_mod3,
                result.writes_status, result.status_504d80,
                result.destination) == (value, value % 3, 1, status, 0x504D80)

    result = build(-1)
    assert (result.random_value, result.remainder_mod3,
            result.writes_status, result.status_504d80,
            result.destination) == (-1, -1, 0, 0, 0)

print("recovered 0x82600 random-status vectors: ok")

listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, instruction in (
        ("82604:", "remi 3,g0,g0"),
        ("82608:", "cmpibe 1,g0,0x82630"),
        ("8260c:", "cmpibl 1,g0,0x82618"),
        ("82610:", "cmpibe 0,g0,0x82620"),
        ("82618:", "cmpibe 2,g0,0x82640"),
        ("82624:", "st g2,0x504d80"),
        ("82634:", "st g3,0x504d80"),
        ("82644:", "st g2,0x504d80")):
    assert any(address in line and instruction in line for line in listing)

print("recovered 0x82600 random-status listing evidence: ok")
