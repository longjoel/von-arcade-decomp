#!/usr/bin/env python3
"""Validate the runnable 0x32810 dispatch+integrator backbone."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_object_update_run_32810.c"

OBJECT_SIZE = 0x600


def u32(buf, offset):
    return ctypes.c_uint32.from_buffer(buf, offset).value


def set_u32(buf, offset, value):
    ctypes.c_uint32.from_buffer(buf, offset).value = value


def set_u16(buf, offset, value):
    ctypes.c_uint16.from_buffer(buf, offset).value = value


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "object-update-run.so"
    subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                    "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
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
    set_u32(buf, 0x08, 100)
    set_u32(buf, 0x10, 200)
    set_u32(buf, 0x1C8, 5)
    set_u32(buf, 0x1CC, 0xFFFFFFFF)
    set_u16(buf, 0x1B2, 3)
    set_u16(buf, 0x172, 5)
    run(ctypes.byref(buf))
    assert (u32(buf, 0x08), u32(buf, 0x10)) == (105, 199)

    # Out-of-range action/state still integrate (dispatch is gated, not fatal).
    set_u32(buf, 0x08, 0)
    set_u32(buf, 0x10, 0)
    set_u32(buf, 0x1C8, 1)
    set_u32(buf, 0x1CC, 2)
    set_u16(buf, 0x1B2, 99)
    set_u16(buf, 0x172, 99)
    run(ctypes.byref(buf))
    assert (u32(buf, 0x08), u32(buf, 0x10)) == (1, 2)

    # Negative state high bit is rejected by the guard but integration runs.
    set_u32(buf, 0x08, 10)
    set_u32(buf, 0x10, 20)
    set_u32(buf, 0x1C8, 4)
    set_u32(buf, 0x1CC, 4)
    set_u16(buf, 0x1B2, 0)
    set_u16(buf, 0x172, 0x8000)
    run(ctypes.byref(buf))
    assert (u32(buf, 0x08), u32(buf, 0x10)) == (14, 24)

print("PASS: 0x32810 runnable dispatch + integrator backbone")
