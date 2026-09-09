#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_calibration_secondary_partition_916e0.c"
listing = (root / "von/build/disasm/vonj-maincpu.lst").read_text()
for address, text in (("916e0", "ldq"), ("9174c", "lda"),
                      ("917b8", "lda"), ("91818", "lda"),
                      ("918a0", "lda"), ("919e0", "ldq"),
                      ("91a74", "movr")):
    assert any(address + ":" in line and text in line for line in listing.splitlines())


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "source_value", "branch_target", "branch_class")]


arms = (
    (0x8b, 0x91a74), (0x9f, 0x9174c), (0xb3, 0x917b8),
    (0xb8, 0x91a74), (0xcc, 0x91818), (0xf4, 0x91850),
    (0x108, 0x91878), (0x11c, 0x918a0), (0x1f8, 0x918f8),
    (0x234, 0x91920), (0x270, 0x91940), (0x284, 0x91964),
    (0x2c0, 0x9198c), (0x2d4, 0x919b0), (0x310, 0x919d0),
    (0x315, 0x91a74), (0x379, 0x919e0), (0x380, 0x91a74),
)

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "partition.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    function = ctypes.CDLL(str(library)).recovered_geometry_calibration_secondary_partition_916e0
    function.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]
    plan = Plan()
    for source_value, target in arms:
        function(source_value, ctypes.byref(plan))
        assert (plan.source_value, plan.branch_target) == (source_value, target)
    function(0x8a, ctypes.byref(plan))
    assert plan.branch_target == 0x91a74
    function(0x316, ctypes.byref(plan))
    assert plan.branch_target == 0x919e0

print("recovered geometry 0x916e0 threshold-partition fixture: ok")
