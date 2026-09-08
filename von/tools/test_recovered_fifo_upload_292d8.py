#!/usr/bin/env python3
"""Validate the recovered 0x292d8 geometry-port word pump plan."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("select_address", ctypes.c_uint32),
        ("select_value", ctypes.c_uint32),
        ("port_address", ctypes.c_uint32),
        ("header_words", ctypes.c_uint32 * 2),
        ("pair_count", ctypes.c_uint32),
        ("words_per_pair", ctypes.c_uint32),
        ("words_total", ctypes.c_uint32),
        ("saves_return_link", ctypes.c_uint32),
        ("clears_g14", ctypes.c_uint32),
    ]


class ProfileUploadPlan(ctypes.Structure):
    _fields_ = [
        ("prefix_address", ctypes.c_uint32 * 13),
        ("prefix_value", ctypes.c_uint32 * 13),
        ("prefix_count", ctypes.c_uint32),
        ("upload_header", ctypes.c_uint32 * 2),
        ("upload_pair_count", ctypes.c_uint32),
        ("upload_source", ctypes.c_uint32),
        ("post_select_address", ctypes.c_uint32),
        ("post_select_value", ctypes.c_uint32),
        ("post_port_value", ctypes.c_uint32 * 4),
        ("post_command_address", ctypes.c_uint32),
        ("post_command_value", ctypes.c_uint32),
        ("finish_helper", ctypes.c_uint32),
    ]


class ProfileUploadVariantPlan(ctypes.Structure):
    _fields_ = [
        ("write_address", ctypes.c_uint32 * 17),
        ("write_value", ctypes.c_uint32 * 17),
        ("write_count", ctypes.c_uint32),
        ("upload_header", ctypes.c_uint32 * 2),
        ("upload_pair_count", ctypes.c_uint32),
        ("upload_source", ctypes.c_uint32),
        ("finish_helper", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "fifo-upload.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_fifo_upload_292d8.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_fifo_upload_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.POINTER(Plan)]
    profile_fn = lib.recovered_geometry_profile_upload_plan
    profile_fn.argtypes = [ctypes.POINTER(ProfileUploadPlan)]
    variant_fn = lib.recovered_geometry_profile_upload_variant_plan
    variant_fn.argtypes = [ctypes.POINTER(ProfileUploadVariantPlan)]

    # The 0x294b0 setup call writes headers (0, 32) then 64 table words.
    plan = Plan()
    plan_fn(0, 32, ctypes.byref(plan))
    assert (plan.select_address, plan.select_value,
            plan.port_address) == (0x00800060, 0x606, 0x00804000)
    assert list(plan.header_words) == [0, 32]
    assert (plan.pair_count, plan.words_per_pair,
            plan.words_total) == (32, 2, 64)
    assert (plan.saves_return_link, plan.clears_g14) == (1, 1)

    plan_fn(7, 1, ctypes.byref(plan))
    assert list(plan.header_words) == [7, 1]
    assert plan.words_total == 2

    profile = ProfileUploadPlan()
    profile_fn(ctypes.byref(profile))
    assert profile.prefix_count == 13
    assert list(profile.prefix_address) == [
        0x800160, 0x804000, 0x800070, 0x804000, 0x800080,
        0x804000, 0x800030, 0x804000, 0x804004, 0x804008,
        0x80400c, 0x804000, 0x804000,
    ]
    assert list(profile.prefix_value) == [
        0x1616, 0x47800000, 0x707, 3, 0x808, 0x41004000,
        0x303, 0x80, 0x1f40204, 0xf80140, 0xf80140,
        0xf80140, 0xf80140,
    ]
    assert (list(profile.upload_header), profile.upload_pair_count,
            profile.upload_source) == ([0, 32], 32, 0x293b0)
    assert (profile.post_select_address, profile.post_select_value,
            list(profile.post_port_value), profile.post_command_address,
            profile.post_command_value, profile.finish_helper) == (
        0x800090, 0x909, [0x44160000, 0x44160000, 0, 0],
        0x8000a0, 0xa0a, 0x28d30)

    variant = ProfileUploadVariantPlan()
    variant_fn(ctypes.byref(variant))
    assert variant.write_count == 17
    assert list(variant.write_address) == [
        0x800160, 0x804000, 0x800070, 0x804000, 0x800080,
        0x804000, 0x800030, 0x804000, 0x804004, 0x804008,
        0x80400c, 0x804000, 0x804000, 0x8000a0, 0x804000,
        0x804004, 0x804000,
    ]
    assert list(variant.write_value) == [
        0x1616, 0x46000000, 0x707, 3, 0x808, 0x41004000,
        0x303, 0x80, 0x1f40204, 0xf80140, 0xf80140,
        0xf80140, 0xf80140, 0xa0a, 0x3f333333, 0xbf000000,
        0x3f000000,
    ]
    assert (list(variant.upload_header), variant.upload_pair_count,
            variant.upload_source, variant.finish_helper) == (
        [0, 32], 32, 0x293b0, 0x28d30)

print("PASS: 0x292d8 FIFO word pump plan")
