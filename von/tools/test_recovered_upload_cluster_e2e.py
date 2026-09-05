#!/usr/bin/env python3
"""End-to-end lifecycle of the 0x29c08/0x29d50 upload cluster.

Chains the recovered pure units the way the listing executes them:
seed (0x29d2c) -> clamp (0x29c08) parks the uploader -> reseed ->
prologue guard and bank select (0x29d50) -> direct or blend stride
schedule over 8 passes -> per-texel kernel and loop trip counts.
"""
import ctypes
import pathlib
import subprocess
import tempfile

I960 = pathlib.Path(__file__).parents[1] / "i960"
SOURCES = [
    "recovered_upload_state_init_29d2c.c",
    "recovered_clamp_store_29c08.c",
    "recovered_upload_select_29d50.c",
    "recovered_blend_kernel_29dec.c",
    "recovered_blend_loop_schedule_29e68.c",
    "recovered_blend_stride_schedule_29e4c.c",
    "recovered_direct_stride_schedule_29f60.c",
]
M32 = 0x100000000


class SeedPlan(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in
                ("value_addr", "mode_addr", "counter_addr",
                 "value_stored", "mode_stored")] + [
                ("counter_stored", ctypes.c_int32),
                ("uploader_active", ctypes.c_int32)]


class ClampPlan(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in
                ("value_addr", "zero_addr0", "zero_addr1")] + [
                ("clamp_max", ctypes.c_int32),
                ("stored", ctypes.c_int32)]


class SelectPlan(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in
                ("counter_addr", "mode_addr")] + [
                ("active", ctypes.c_int32),
                ("old_counter", ctypes.c_int32),
                ("next_counter", ctypes.c_int32)] + [
                (n, ctypes.c_uint32) for n in
                ("src0_addr", "dst0_addr", "src1_addr", "dst1_addr",
                 "src2_addr", "dst2_addr", "mode")] + [
                ("direct_path", ctypes.c_int32)]


class LoopPlan(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in
                ("iterations", "stores", "pointer_advance",
                 "src_end", "dst_end")]


class BlendStridePlan(ctypes.Structure):
    _fields_ = ([("mode_addr", ctypes.c_uint32),
                 ("outer_iterations", ctypes.c_uint32),
                 ("plane_fade", ctypes.c_uint32 * 3),
                 ("pass_advance0", ctypes.c_uint32),
                 ("pass_advance1", ctypes.c_uint32),
                 ("pass_advance2", ctypes.c_uint32)] +
                [(n, ctypes.c_uint32) for n in
                 ("src0_end", "dst0_end", "src1_end", "dst1_end",
                  "src2_end", "dst2_end")])


class DirectStridePlan(ctypes.Structure):
    _fields_ = ([("fade_addr", ctypes.c_uint32),
                 ("use_fade_form", ctypes.c_int32),
                 ("factor", ctypes.c_uint32),
                 ("outer_iterations", ctypes.c_uint32),
                 ("pass_advance", ctypes.c_uint32)] +
                [(n, ctypes.c_uint32) for n in
                 ("src0_end", "dst0_end", "src1_end", "dst1_end",
                  "src2_end", "dst2_end")])


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "upload-cluster.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2"] +
                   [str(I960 / s) for s in SOURCES] +
                   ["-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))

    seed_fn = lib.recovered_upload_state_init_plan
    seed_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(SeedPlan)]
    clamp_fn = lib.recovered_clamp_store_plan
    clamp_fn.argtypes = [ctypes.c_int32, ctypes.POINTER(ClampPlan)]
    select_fn = lib.recovered_upload_select_plan
    select_fn.argtypes = [ctypes.c_int32, ctypes.c_uint32,
                          ctypes.POINTER(SelectPlan)]
    mul_fn = lib.recovered_blend_kernel_mul
    mul_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    mul_fn.restype = ctypes.c_uint32
    fade_fn = lib.recovered_blend_kernel_fade
    fade_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    fade_fn.restype = ctypes.c_uint32
    loop_fn = lib.recovered_blend_loop_schedule_plan
    loop_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.POINTER(LoopPlan)]
    blend_fn = lib.recovered_blend_stride_schedule_plan
    blend_fn.argtypes = ([ctypes.c_uint32] * 7 +
                         [ctypes.POINTER(BlendStridePlan)])
    direct_fn = lib.recovered_direct_stride_schedule_plan
    direct_fn.argtypes = ([ctypes.c_int32] + [ctypes.c_uint32] * 6 +
                          [ctypes.POINTER(DirectStridePlan)])

    # 1. Seed presets counter 4: the first upload call is already active.
    seed = SeedPlan()
    seed_fn(0x29C4C, ctypes.byref(seed))
    assert seed.counter_stored == 4 and seed.uploader_active == 1

    # 2. A clamp parks the uploader by zeroing its counter/mode slots.
    clamp = ClampPlan()
    clamp_fn(0x50, ctypes.byref(clamp))
    assert clamp.stored == 0x50
    assert (clamp.zero_addr0, clamp.zero_addr1) == (0x51A264, 0x51A268)

    # 3. Reseed, then the prologue selects bank 4 and takes direct path.
    seed_fn(0x29C4C, ctypes.byref(seed))
    select = SelectPlan()
    select_fn(seed.counter_stored, 0, ctypes.byref(select))
    assert select.active == 1 and select.direct_path == 1
    assert select.next_counter == 5
    bank = 4 << 12
    ptrs = (select.src0_addr, select.dst0_addr, select.src1_addr,
            select.dst1_addr, select.src2_addr, select.dst2_addr)
    assert ptrs == (0x01810100 + bank, 0x01810000 + bank,
                    0x01814100 + bank, 0x01814000 + bank,
                    0x01818100 + bank, 0x01818000 + bank)

    # 4. Direct run with fade 0x80: scale form, every pair spans a bank.
    direct = DirectStridePlan()
    direct_fn(0x80, *ptrs, ctypes.byref(direct))
    assert direct.use_fade_form == 0 and direct.factor == 0x180
    for end, start in zip((direct.src0_end, direct.dst0_end,
                           direct.src1_end, direct.dst1_end,
                           direct.src2_end, direct.dst2_end), ptrs):
        assert end == (start + 0x1000) % M32

    # 5. Blend run with mode 0b101: planes 0/2 fade, plane 1 scales.
    blend = BlendStridePlan()
    blend_fn(*ptrs, 0b101, ctypes.byref(blend))
    assert tuple(blend.plane_fade) == (1, 0, 1)
    assert (blend.src0_end - ptrs[0]) % M32 == 0x1000
    assert (blend.src1_end - ptrs[2]) % M32 == 0x1000
    assert (blend.src2_end - ptrs[4]) % M32 == 8 * 0x380

    # 6. One inner loop contributes 32 kernel texels over 0x80 bytes.
    loop = LoopPlan()
    loop_fn(ptrs[0], ptrs[1], ctypes.byref(loop))
    assert (loop.iterations, loop.stores) == (32, 32)
    assert (loop.src_end - ptrs[0]) % M32 == 0x80

    # 7. Kernel forms agree with the selected loop forms on real texels.
    assert mul_fn(0x00123456, 0x180) == \
        (((0x180 * (0x00123456 & 0xFF00FF)) % M32) >> 8)
    masked = 0x00123456 & 0xFF00FF
    assert fade_fn(0x00123456, 0x80) == \
        (masked + (((0x80 * ((masked - 0xFF00FF) % M32)) % M32) >> 8)) % M32

    # 8. Store budget for a full run: 8 passes x 3 planes x 32 texels.
    assert direct.outer_iterations * 3 * loop.stores == 768

print("PASS: 0x29c08/0x29d50 upload cluster end to end")
