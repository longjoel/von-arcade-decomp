#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Write(ctypes.Structure):
    _fields_ = [("address", ctypes.c_uint32), ("value", ctypes.c_uint32)]


class Result(ctypes.Structure):
    _fields_ = [("input_word", ctypes.c_uint32),
                ("tagged_input_word", ctypes.c_uint32),
                ("setup", Write * 18),
                ("setup_count", ctypes.c_uint32),
                ("fifo_prefix", ctypes.c_uint32 * 6),
                ("fifo_prefix_count", ctypes.c_uint32),
                ("scene_count_address", ctypes.c_uint32),
                ("record_table_address", ctypes.c_uint32),
                ("first_record_index", ctypes.c_int32),
                ("object_dispatch_target", ctypes.c_uint32),
                ("first_loop_target", ctypes.c_uint32),
                ("mode_address", ctypes.c_uint32),
                ("final_return_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-scene-prologue-") as d:
        so = Path(d) / "scene-prologue.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_status_scene_prologue_e79f0.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_status_scene_prologue_e79f0
        fn.argtypes = [ctypes.c_uint32]
        fn.restype = Result
        out = fn(0x12)
        assert out.tagged_input_word == 0x92
        assert out.setup_count == 18
        assert [(out.setup[i].address, out.setup[i].value) for i in range(3)] == [
            (0x800070, 0x707), (0x804000, 3), (0x800030, 0x303)]
        assert (out.setup[3].value, out.setup[4].value,
                out.setup[5].value, out.setup[9].value) == (0x92, 0x1f40204, 0xf80140, 0x909)
        assert list(out.fifo_prefix) == [8, 16, 18, 0, 0, 0x43000000]
        assert (out.scene_count_address, out.record_table_address,
                out.first_record_index, out.object_dispatch_target,
                out.first_loop_target, out.mode_address,
                out.final_return_target) == (
            0x5783c0, 0x5784e4, -5, 0xe7390, 0xe7b14, 0x5783c4, 0xe9138)
        print("PASS: 0xe79f0 status-scene prologue")


if __name__ == "__main__":
    main()
