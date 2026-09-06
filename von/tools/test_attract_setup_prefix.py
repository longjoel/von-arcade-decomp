#!/usr/bin/env python3
"""Pin the title-to-attract parser-boundary fixture.

The original 45-second no-input attract capture and the reconstructed
45-second run share an identical 9-opcode display-list setup grammar
(0b001616 through 08001010). At event 9 they diverge: the original emits
a second, reordered setup block while the reconstructed seed proceeds to
matrix records -- confounded by scene content (attract demo vs seeded
match-entry), so the divergence is recorded, not chased into the image.

Opcode events are inline (build/disasm traces are generated, never
repository data): original lines 1-10 of the vonj_geometry_opcode stream
from the no-input attract capture; reconstructed lines 229-238 (after 228
sentinel spins) from the vonjdev run.
"""

from compare_geometry_parser_opcode_prefix import load
from pathlib import Path
import tempfile

ORIGINAL_OPCODES = """\
[:] vonj_geometry_opcode: time=30.004784 read=00010000 opcode=0b001616 p0=47800000 p1=03800707 p2=00000003 p3=04000808
[:] vonj_geometry_opcode: time=30.004784 read=00010000 opcode=03800707 p0=00000003 p1=04000808 p2=41004000 p3=01800303
[:] vonj_geometry_opcode: time=30.004784 read=00010000 opcode=04000808 p0=41004000 p1=01800303 p2=00000080 p3=01f40204
[:] vonj_geometry_opcode: time=30.004784 read=00010000 opcode=01800303 p0=00000080 p1=01f40204 p2=00f80140 p3=00f80140
[:] vonj_geometry_opcode: time=30.004784 read=00010000 opcode=03000606 p0=00000000 p1=00000020 p2=04ffffff p3=3f800000
[:] vonj_geometry_opcode: time=30.004784 read=00010000 opcode=04800909 p0=44160000 p1=44160000 p2=05000a0a p3=00000000
[:] vonj_geometry_opcode: time=30.004784 read=00010000 opcode=05000a0a p0=00000000 p1=00000000 p2=3f800000 p3=02000404
[:] vonj_geometry_opcode: time=30.004784 read=00010000 opcode=02000404 p0=00800000 p1=00000060 p2=000080c0 p3=00000000
[:] vonj_geometry_opcode: time=30.004784 read=00010000 opcode=08001010 p0=00000000 p1=0b001616 p2=46000000 p3=03800707
[:] vonj_geometry_opcode: time=30.004784 read=00010000 opcode=0b001616 p0=46000000 p1=03800707 p2=00000003 p3=04000808
"""

RECONSTRUCTED_OPCODES = """\
[:] vonj_geometry_opcode: time=33.968336 read=00010000 opcode=0b001616 p0=47800000 p1=03800707 p2=00000003 p3=04000808
[:] vonj_geometry_opcode: time=33.968336 read=00010000 opcode=03800707 p0=00000003 p1=04000808 p2=41004000 p3=01800303
[:] vonj_geometry_opcode: time=33.968336 read=00010000 opcode=04000808 p0=41004000 p1=01800303 p2=00000080 p3=01f40204
[:] vonj_geometry_opcode: time=33.968336 read=00010000 opcode=01800303 p0=00000080 p1=01f40204 p2=00f80140 p3=00f80140
[:] vonj_geometry_opcode: time=33.968336 read=00010000 opcode=03000606 p0=00000000 p1=00000000 p2=04800909 p3=44160000
[:] vonj_geometry_opcode: time=33.968336 read=00010000 opcode=04800909 p0=44160000 p1=44160000 p2=05000a0a p3=00000000
[:] vonj_geometry_opcode: time=33.968336 read=00010000 opcode=05000a0a p0=00000000 p1=00000000 p2=3f800000 p3=02000404
[:] vonj_geometry_opcode: time=33.968336 read=00010000 opcode=02000404 p0=00800000 p1=00000000 p2=08001010 p3=00000000
[:] vonj_geometry_opcode: time=33.968336 read=00010000 opcode=08001010 p0=00000000 p1=05800000 p2=3e23d70a p3=00000000
[:] vonj_geometry_opcode: time=33.968336 read=00010000 opcode=05800000 p0=3e23d70a p1=00000000 p2=00000000 p3=00000000
"""

SETUP_PREFIX = [
    0x0B001616,
    0x03800707,
    0x04000808,
    0x01800303,
    0x03000606,
    0x04800909,
    0x05000A0A,
    0x02000404,
    0x08001010,
]


def _load(text, limit):
    handle = tempfile.NamedTemporaryFile("w", suffix=".trace", delete=False)
    handle.write(text)
    handle.close()
    return load(Path(handle.name), limit)


def test_shared_setup_prefix_parses_identically():
    assert _load(ORIGINAL_OPCODES, 9) == SETUP_PREFIX
    assert _load(RECONSTRUCTED_OPCODES, 9) == SETUP_PREFIX


def test_first_divergence_is_recorded():
    original = _load(ORIGINAL_OPCODES, 10)
    reconstructed = _load(RECONSTRUCTED_OPCODES, 10)
    assert original[:9] == reconstructed[:9]
    assert original[9] == 0x0B001616
    assert reconstructed[9] == 0x05800000


if __name__ == "__main__":
    test_shared_setup_prefix_parses_identically()
    test_first_divergence_is_recorded()
    print("attract setup prefix fixture: PASS")
