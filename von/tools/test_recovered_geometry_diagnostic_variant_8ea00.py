#!/usr/bin/env python3
import ctypes, pathlib, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_geometry_diagnostic_variant_8ea00.c"

class Input(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "record_word", "raw_word_0", "raw_word_1", "raw_word_2",
        "raw_word_3", "raw_word_4", "frame_readback")]
class Plan(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32 * 16), ("fifo_count", ctypes.c_uint32),
                ("masked_word_0", ctypes.c_uint32), ("masked_word_1", ctypes.c_uint32),
                ("masked_word_2", ctypes.c_uint32), ("control_value", ctypes.c_uint32)]
class WindowPlan(ctypes.Structure):
    _fields_ = [("state_word", ctypes.c_uint32), ("window_word", ctypes.c_uint32 * 4),
                ("control_address", ctypes.c_uint32), ("control_value", ctypes.c_uint32),
                ("next_target", ctypes.c_uint32)]
class FixedPlan(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32 * 11), ("fifo_count", ctypes.c_uint32),
                ("frame_readback", ctypes.c_uint32)]
class FinalPlan(ctypes.Structure):
    _fields_ = [("state_word", ctypes.c_uint32), ("window_word", ctypes.c_uint32 * 4),
                ("control_address", ctypes.c_uint32), ("control_value", ctypes.c_uint32),
                ("completion_word", ctypes.c_uint32 * 2)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "diagnostic_variant.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-I", str(root / "von/i960"),
                    "-o", str(library), str(source)], check=True)
    fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_8ea00
    fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Plan)]
    sample = Input(0x11111111, 0xaaaa0001, 0xbbbb0002, 0xcccc0003,
                   0x22222222, 0x33333333, 0xdeadbeef)
    plan = Plan(); fn(ctypes.byref(sample), ctypes.byref(plan))
    assert list(plan.fifo_word) == [5, 19, 0x40000000, 0x40000000, 0x40000000,
                                    5, 44, 0x11111111, 0x22222222, 0x33333333,
                                    1, 2, 44, 3, 44, 0xdeadbeef]
    assert plan.fifo_count == 16 and plan.control_value == 0x101
    assert (plan.masked_word_0, plan.masked_word_1, plan.masked_word_2) == (1, 2, 3)
    window_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_window_8ec84
    window_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(WindowPlan)]
    window = WindowPlan(); window_fn(0, 0x12345678, ctypes.byref(window))
    assert list(window.window_word) == [0x403800, 0x403930, 0x8500a2, 0]
    assert (window.control_address, window.control_value, window.next_target) == (
        0x800010, 0x101, 0x8ed7c)
    window_fn(1, 0x12345678, ctypes.byref(window))
    assert list(window.window_word) == [0x403800, 0x5afede, 0x8500a2, 0x12345678]
    window2_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_window_8ee14
    window2_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(WindowPlan)]
    window2_fn(0, 0x12345678, ctypes.byref(window))
    assert list(window.window_word) == [0x403800, 0x403930, 0x8500a2, 0]
    assert window.next_target == 0x8eeb4
    fixed_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_fixed_8ed7c
    fixed_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(FixedPlan)]
    fixed = FixedPlan(); fixed_fn(0xdeadbeef, ctypes.byref(fixed))
    assert list(fixed.fifo_word) == [6, 5, 44, 0x40c01a37, 0x413672b0,
                                     0x3f3a9931, 0x3511, 0x1084, 0xf3e7,
                                     44, 0xdeadbeef]
    assert fixed.fifo_count == 11 and fixed.frame_readback == 0xdeadbeef
    fixed2_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_fixed_8eeb4
    fixed2_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(FixedPlan)]
    fixed2 = FixedPlan(); fixed2_fn(0xdeadbeef, ctypes.byref(fixed2))
    assert list(fixed2.fifo_word) == [6, 5, 44, 0xc0c01a37, 0x413672b0,
                                      0x3f3a9931, 0x3511, 0xef7c, 0xc19,
                                      44, 0xdeadbeef]
    assert fixed2.fifo_count == 11 and fixed2.frame_readback == 0xdeadbeef
    final_fn = ctypes.CDLL(str(library)).recovered_geometry_diagnostic_variant_final_8ef48
    final_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(FinalPlan)]
    final = FinalPlan(); final_fn(0, 0x12345678, ctypes.byref(final))
    assert list(final.window_word) == [0x45e76c, 0x45ec4c, 0x8b518a, 0x12345678]
    assert (final.control_address, final.control_value,
            list(final.completion_word)) == (0x800010, 0x101, [6, 6])
    final_fn(1, 0x12345678, ctypes.byref(final))
    assert list(final.window_word) == [0x45e76c, 0x5baf2a, 0x8b518a, 0x12345678]
print("recovered geometry 0x8ea00 diagnostic-variant prefix: ok")
