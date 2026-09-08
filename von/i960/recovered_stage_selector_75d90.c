/* Stage selector core, i960 routine at 0x00075d90 (caller 0x00027668).
 *
 * Decoded from von/build/disasm/vonj-maincpu.lst. Operand order follows
 * the observed convention (arithmetic dst = src2 - src1, proved by the
 * r4 = 0 - 1 = 0xffffffff sentinel at 0x75f40; compare flags = src1 -
 * src2, proved by the 0x504dc0 clamp below). Signed/unsigned is
 * indistinguishable on all live inputs (ordinals 0..4, small positive
 * words), so the model uses signed 32-bit compares like the listing's
 * ge/l/bl mnemonics.
 *
 * Live truth table (fresh-NVRAM replay of
 * von/captures/vonj-20260907T211227Z/inp/stage3-fleet; mode byte sampled
 * as 2 during every setup window, 255 at boot):
 *
 * stage  idx  g6  g7  divword  0x504dbc  0x504dc0
 * S1     0    1   30  30       3         83
 * S2     1    2/3 30  120      12        92
 * S3     2    8   30  320/280  32/28     112/108
 * S4     3    32  30  1280     128       208
 * S5     4    64  30  2560     256       300 (clamped)
 *
 * - g7 (0x75d90): mode byte @0x1d00021 selects 8/30/2 for 1/2/3,
 *   else 4. All four arms are live encodings (no dead code here).
 * - index (0x75dd0): g5 + [0x503a80] with g5 = [0x503a94] when
 *   [0x5039f4] == 4 else 0, plus 1 when [0x503a6c] > 0.
 * - g6 (table @0x75e18): 1, 2/3 (sub-checks through the g0 bout
 *   struct: 2 when the loaded check word is 1, 2 or 5), 8, 32,
 *   64, 64, 99. Index > 6 reads past the table (never live).
 * - stamp (0x75e84): takeover (signed [0x503a80] > [0x509b80], or
 *   [0x503a74] != 0) yields g6 * g7 directly; otherwise the divisor
 *   word at absolute address 9 * g6 * g7 is doubled and divided
 *   signed by 20. S3 continues re-roll that word (320 -> 280).
 * - 0x504dc0 (0x75e84 tail): min(0x504dbc + 0x50, 300). The bge
 *   skips the 300 overwrite exactly when 300 >= dbc + 0x50, so S5
 *   (336) is the only stage that clamps. Verified in spawn RAM
 *   dumps d1-d4 (112/108/108/208).
 * - register passthrough: g14 lands in 19 cells (0x504dc4, 0x504d64
 *   16-bit, 0x504d68, 0x504d6c 16-bit, 0x504d70/74/7c/80/88/94/98/
 *   9c/a0/a4/a8/b4/c8/cc/d0), r4 - 1 in 0x504d8c/90 (live goldens
 *   g14 = 0, r4 = 0, hence d88 = 0 and the -1 pair in every dump).
 * - constants: [0x504d60] = 0x43200000 (160.0f), [0x504d78] =
 *   [0x504d84] = [0x504dac] = [0x504db0] = 1, [0x504db8] = 5.
 *   The [0x504d88] = 30 store is transient (overwritten by g14).
 *
 * The row-copy tail from 0x75fe4 is modeled by
 * recovered_object_state_descriptor_75f00.c. The nested call at 0x76030
 * remains outside this selector slice.
 */

typedef unsigned int u32;
typedef signed int s32;

u32 stage_selector_g7(u32 mode)
{
    if (mode == 1)
        return 8U;
    if (mode == 2)
        return 30U;
    if (mode == 3)
        return 2U;
    return 4U;
}

u32 stage_selector_index(u32 f4, u32 a94, u32 a6c, u32 a80)
{
    u32 g5 = (f4 == 4U) ? a94 : 0U;
    if ((s32)a6c > 0)
        g5 += 1U;
    return g5 + a80;
}

u32 stage_selector_g6(u32 idx, u32 subcheck)
{
    switch (idx) {
    case 0U:
        return 1U;
    case 1U:
        return (subcheck == 1U || subcheck == 2U || subcheck == 5U) ? 2U : 3U;
    case 2U:
        return 8U;
    case 3U:
        return 32U;
    case 4U:
    case 5U:
        return 64U;
    default:
        return 99U;
    }
}

u32 stage_selector_stamp(u32 g6, u32 g7, u32 a80, u32 b80, u32 a74,
                         u32 divword, u32 *dc0)
{
    u32 prod = g6 * g7;
    u32 dbc;
    if ((s32)a80 > (s32)b80 || a74 != 0U) {
        dbc = prod;
    } else {
        dbc = (u32)(((s32)(divword << 1)) / 20);
    }
    {
        u32 sum = dbc + 0x50U;
        *dc0 = (300U >= sum) ? sum : 300U;
    }
    return dbc;
}

typedef struct {
    u32 d64, d68, d6c;
    u32 d70, d74, d7c, d80, d88;
    u32 dc4;
    u32 d8c, d90;
    u32 d94, d98, d9c, da0, da4, da8, db4, dc8, dcc, dd0;
    u32 d60, d78, d84, dac, db0, db8;
} stage_selector_tail_out;

void stage_selector_tail(u32 g14, u32 r4, stage_selector_tail_out *o)
{
    u32 half = g14 & 0xffffU;
    u32 rm1 = r4 - 1U;
    o->d64 = half;
    o->d68 = g14;
    o->d6c = half;
    o->d70 = g14;
    o->d74 = g14;
    o->d7c = g14;
    o->d80 = g14;
    o->d88 = g14;
    o->dc4 = g14;
    o->d8c = rm1;
    o->d90 = rm1;
    o->d94 = g14;
    o->d98 = g14;
    o->d9c = g14;
    o->da0 = g14;
    o->da4 = g14;
    o->da8 = g14;
    o->db4 = g14;
    o->dc8 = g14;
    o->dcc = g14;
    o->dd0 = g14;
    o->d60 = 0x43200000U;
    o->d78 = 1U;
    o->d84 = 1U;
    o->dac = 1U;
    o->db0 = 1U;
    o->db8 = 5U;
}
