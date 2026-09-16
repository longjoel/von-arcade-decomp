#!/usr/bin/env python3
"""Validate the runnable 0x32810 dispatch+integrator backbone."""

import ctypes
import pathlib
import struct
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_object_update_run_32810.c"
LOCOMOTION = [
    ROOT / "von/i960/recovered_locomotion_states.c",
    ROOT / "von/i960/recovered_locomotion_actions.c",
    ROOT / "von/i960/recovered_state_attack_arms.c",
    ROOT / "von/i960/recovered_state_locomotion_arms.c",
    ROOT / "von/i960/recovered_state_dash_20.c",
]

OBJECT_SIZE = 0x600


def fbits(value):
    return struct.unpack("<I", struct.pack("<f", value))[0]


def u32(buf, offset):
    return ctypes.c_uint32.from_buffer(buf, offset).value


def set_u32(buf, offset, value):
    ctypes.c_uint32.from_buffer(buf, offset).value = value


def set_u16(buf, offset, value):
    ctypes.c_uint16.from_buffer(buf, offset).value = value


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "object-update-run.so"
    subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                    "-shared", "-fPIC", "-O2", SOURCE, *LOCOMOTION, "-o", library], check=True)
    dll = ctypes.CDLL(str(library))

    run = dll.recovered_object_update_32810_run
    run.argtypes = [ctypes.c_void_p]
    action_count = dll.recovered_object_update_32810_action_count
    action_count.restype = ctypes.c_uint32
    state_count = dll.recovered_object_update_32810_state_count
    state_count.restype = ctypes.c_uint32

    assert action_count() == 14
    assert state_count() == 43

    buf = (ctypes.c_ubyte * OBJECT_SIZE)()
    set_u32(buf, 0x08, fbits(100.0))
    set_u32(buf, 0x10, fbits(200.0))
    set_u32(buf, 0x1C8, fbits(5.0))
    set_u32(buf, 0x1CC, fbits(-1.0))
    set_u16(buf, 0x1B2, 3)
    set_u16(buf, 0x172, 22)
    run(ctypes.byref(buf))
    assert (u32(buf, 0x08), u32(buf, 0x10)) == (fbits(105.0), fbits(199.0))

    # Out-of-range action/state still integrate (dispatch is gated, not fatal).
    set_u32(buf, 0x08, fbits(0.0))
    set_u32(buf, 0x10, fbits(0.0))
    set_u32(buf, 0x1C8, fbits(1.0))
    set_u32(buf, 0x1CC, fbits(2.0))
    set_u16(buf, 0x1B2, 99)
    set_u16(buf, 0x172, 99)
    run(ctypes.byref(buf))
    assert (u32(buf, 0x08), u32(buf, 0x10)) == (fbits(1.0), fbits(2.0))

    # Negative state high bit is rejected by the guard but integration runs.
    # Use action 1 (stub arm) so the test does not invoke the absolute-address
    # locomotion action 0 on the host.
    set_u32(buf, 0x08, fbits(10.0))
    set_u32(buf, 0x10, fbits(20.0))
    set_u32(buf, 0x1C8, fbits(4.0))
    set_u32(buf, 0x1CC, fbits(4.0))
    set_u16(buf, 0x1B2, 1)
    set_u16(buf, 0x172, 0x8000)
    run(ctypes.byref(buf))
    assert (u32(buf, 0x08), u32(buf, 0x10)) == (fbits(14.0), fbits(24.0))

print("PASS: 0x32810 runnable dispatch + integrator backbone")
