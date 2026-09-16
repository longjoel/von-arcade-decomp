/*
 * Bounded freestanding runnable recovered-C unit for the i960 locomotion
 * state handlers 31 and 34.
 *
 * Listing spans in von/build/disasm/vonj-maincpu.lst:
 *   0x30660-0x30c1c  state 31 handler (0x32560 slot 33, table word 0x32750)
 *   0x30e40-0x30fec  state 34 handler (0x32560 slot 35, table word 0x32780)
 *
 * The 43-entry 0x32560 update table selects on object+0x172; state 34's clip
 * end stores +0x172 = 31, handing the object back to the state-31 handler
 * (0x30f5c-0x30f70 mov 31,g1 / stos g1,0x172(g0)).
 *
 * Config pointer
 *   st g6,0x6c(g0) at 0x27558 seeds object+0x6c.  The listing reaches the same
 *   block through the absolute slot 0x51ab14 (ld 0x51ab14,g5 at 0x3067c,
 *   0x306a4, 0x306c0, ... and ld 0x51ab14,g7 at 0x30e58, 0x30f94); this unit
 *   reads object+0x6c so it stays freestanding and host-testable.  The absolute
 *   publication cells 0x51ab08/0x51ab0c (pointer scratch dereferenced at
 *   0x3096c and 0x30f3c) and the write-only 0x51ab10/0x51ab12 counters are
 *   file-static stand-ins.
 *
 * State 31 (0x30660)
 *   0x30660-0x307e4  weapon-callback preface.  +0x17e in 1..0x7fff arms the
 *                    +0x174 == 1/2/3 arms, which call cfg+0x3cc/0x3d0/0x3d4 and
 *                    then, when +0x172 == 0, seed +0x18e from cfg+0x5e8..0x608.
 *   0x307e8-0x308b4  +0x170 = 0; publish the cfg+0xf8/0x100/0x108 and
 *                    cfg+0xfc/0x104/0x10c table words selected by +0x17e
 *                    (0 / 1..3 / 4; +0x176 index shifted left 5).
 *   0x308b8-0x30960  +0x17a += 1 and the +0x138/+0x139/+0x13a/+0x13c
 *                    sentinels gated by bit 0 of +0x1de/+0x1dd/+0x1df writing
 *                    +0x174 = 1/2/3/16.
 *   0x30964-0x30ad0  clip scan of the published record count (+4); +0x17e == 3
 *                    classifies +0x102/+0x188 into state 33 or 35, +0x17e == 4
 *                    commits +0x172 = 0 / +0x170 = 1, +0x174 == 16 commits
 *                    +0x172 = 35; otherwise +0x17e += 1 and +0x17a = 0.
 *   0x30ad4-0x30c18  +0x1c4 = cfg+0x56c/0x570/0x574 (default) or the
 *                    cfg+0x578..0x598 tables keyed by +0x174/+0x176.
 *
 * State 34 (0x30e40)
 *   0x30e40-0x30ec4  +0x170 = 0; publish cfg+0x180 and cfg+0x184 (index
 *                    3*+0x176, then *8) to the 0x51ab0c/0x51ab08 cells;
 *                    +0x1c4 = cfg+0x570 (or cfg+0x574 / cfg+0x56c) by +0x176.
 *   0x30ec8-0x30f2c  the same +0x138/+0x139/+0x13a/+0x13c sentinel gate.
 *   0x30f30-0x30fe8  clip scan of the published record count (+4); before the
 *                    end +0x17a += 1, at the end +0x172 = 31, +0x170 = 0,
 *                    +0x17a = 0, +0x17e = 1, +0x1a0 = 0, +0x1a8 = +0x1a9 = 1
 *                    and +0x4e += cfg+0x658.
 *
 * Only the integer loads/stores present in the listing are used; the weapon
 * callbacks are external and are invoked only when their cfg pointer is
 * non-zero, exactly as the cmpibe 0,g4 guards at 0x30688/0x30708/0x30788.
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed int s32;

/* st g6,0x6c(g0) at 0x27558: the config pointer the listing finds at 0x51ab14. */
#define RECOVERED_LOCOMOTION_CONFIG_OFFSET 0x6cU

/* Listing absolute scratch cells, kept file-static so no MMIO is touched. */
static volatile u32 recovered_locomotion_publish_lo;  /* 0x51ab08 */
static volatile u32 recovered_locomotion_publish_hi;  /* 0x51ab0c */
static volatile u16 recovered_locomotion_counter_a;   /* 0x51ab10 */
static volatile u16 recovered_locomotion_counter_b;   /* 0x51ab12 */

static volatile unsigned char *recovered_locomotion_config(
    volatile unsigned char *object)
{
    return (volatile unsigned char *)(unsigned long)
        *(volatile u32 *)(object + RECOVERED_LOCOMOTION_CONFIG_OFFSET);
}

static u32 recovered_locomotion_cfg_u32(const volatile unsigned char *cfg,
                                        u32 offset)
{
    return *(volatile u32 *)(unsigned long)(cfg + offset);
}

static u16 recovered_locomotion_ldos(const volatile unsigned char *object,
                                     u32 offset)
{
    return *(volatile u16 *)(unsigned long)(object + offset);
}

static u8 recovered_locomotion_ldob(const volatile unsigned char *object,
                                    u32 offset)
{
    return *(volatile u8 *)(unsigned long)(object + offset);
}

/*
 * 0x308e8-0x30960 (state 31) and 0x30ec8-0x30f2c (state 34): the weapon
 * sentinels.  Each arm needs the +0x13x byte at 0xff and bit 0 of its +0x1d_x
 * companion set; the fall-through byte +0x13c == 0xff selects 16.  Returns 1
 * and the +0x174 selector when an arm fires, 0 when +0x174 is left alone.
 */
static u32 recovered_locomotion_weapon_gate(
    const volatile unsigned char *object, u32 *selector)
{
    if (recovered_locomotion_ldob(object, 0x13aU) == 0xffU
            && (recovered_locomotion_ldob(object, 0x1dfU) & 1U) != 0U) {
        *selector = 3U;
        return 1U;
    }
    if (recovered_locomotion_ldob(object, 0x138U) == 0xffU
            && (recovered_locomotion_ldob(object, 0x1deU) & 1U) != 0U) {
        *selector = 1U;
        return 1U;
    }
    if (recovered_locomotion_ldob(object, 0x139U) == 0xffU
            && (recovered_locomotion_ldob(object, 0x1ddU) & 1U) != 0U) {
        *selector = 2U;
        return 1U;
    }
    if (recovered_locomotion_ldob(object, 0x13cU) == 0xffU) {
        *selector = 16U;
        return 1U;
    }
    return 0U;
}

/*
 * 0x30ad4-0x30c18: the state-31 +0x1c4 selector, read fresh from +0x174 and
 * +0x176 at 0x30ad4/0x30adc.  +0x174 1/2/3 use the cfg+0x578/0x588/0x594
 * triplets; every other value uses cfg+0x56c/0x570/0x574.
 */
static u32 recovered_locomotion_state31_speed(const volatile unsigned char *cfg,
                                              u32 f174, u32 f176)
{
    if (f174 == 1U) {
        if (f176 == 0U)
            return recovered_locomotion_cfg_u32(cfg, 0x57cU);
        if (f176 == 1U)
            return recovered_locomotion_cfg_u32(cfg, 0x580U);
        return recovered_locomotion_cfg_u32(cfg, 0x578U);
    }
    if (f174 == 2U) {
        if (f176 == 0U)
            return recovered_locomotion_cfg_u32(cfg, 0x588U);
        if (f176 == 1U)
            return recovered_locomotion_cfg_u32(cfg, 0x58cU);
        return recovered_locomotion_cfg_u32(cfg, 0x584U);
    }
    if (f174 == 3U) {
        if (f176 == 0U)
            return recovered_locomotion_cfg_u32(cfg, 0x594U);
        if (f176 == 1U)
            return recovered_locomotion_cfg_u32(cfg, 0x598U);
        return recovered_locomotion_cfg_u32(cfg, 0x590U);
    }
    if (f176 == 0U)
        return recovered_locomotion_cfg_u32(cfg, 0x570U);
    if (f176 == 1U)
        return recovered_locomotion_cfg_u32(cfg, 0x574U);
    return recovered_locomotion_cfg_u32(cfg, 0x56cU);
}

static void recovered_locomotion_state31_commit(
    volatile unsigned char *object, const volatile unsigned char *cfg)
{
    u32 f174 = recovered_locomotion_ldos(object, 0x174U);
    u32 f176 = recovered_locomotion_ldos(object, 0x176U);

    *(volatile u32 *)(object + 0x1c4) = recovered_locomotion_state31_speed(
        cfg, f174, f176);
}

/* 0x30a70-0x30a90: the +0x174 == 16 arm commits +0x172 = 31 + 4 = 35. */
static void recovered_locomotion_state35_commit(volatile unsigned char *object)
{
    *(volatile u16 *)(object + 0x172) = (u16)(31U + 4U);
    *(volatile u16 *)(object + 0x170) = 0U;
    *(volatile u16 *)(object + 0x180) = 0U;
    *(volatile u16 *)(object + 0x186) = 0U;
    *(volatile u16 *)(object + 0x178) = 0U;
    *(volatile u16 *)(object + 0x17a) = 0U;
    *(volatile u16 *)(object + 0x17e) = 0U;
}

/* 0x30ac4-0x30ad0: +0x17e += 1 and +0x17a = 0. */
static void recovered_locomotion_advance_clip(volatile unsigned char *object)
{
    *(volatile u16 *)(object + 0x17e) =
        (u16)(recovered_locomotion_ldos(object, 0x17eU) + 1U);
    *(volatile u16 *)(object + 0x17a) = 0U;
}

void recovered_locomotion_state_31_run(volatile unsigned char *object)
{
    volatile unsigned char *cfg;
    u32 v17e;
    u32 f176;
    u32 cfg_lo;
    u32 cfg_hi;
    u32 old17a;
    u32 selector;
    u32 record;

    cfg = recovered_locomotion_config(object);

    /* 0x30660-0x307e4: +0x17e in 1..0x7fff dispatches +0x174 1/2/3 to the
     * cfg-resident callbacks; a fired callback always leaves through 0x30ad4. */
    v17e = recovered_locomotion_ldos(object, 0x17eU);
    if (v17e != 0U && v17e < 0x8000U) {
        u32 f174 = recovered_locomotion_ldos(object, 0x174U);
        u32 callback = 0U;

        if (f174 == 1U)
            callback = recovered_locomotion_cfg_u32(cfg, 0x3ccU);
        else if (f174 == 2U)
            callback = recovered_locomotion_cfg_u32(cfg, 0x3d0U);
        else if (f174 == 3U)
            callback = recovered_locomotion_cfg_u32(cfg, 0x3d4U);

        if (callback != 0U) {
            ((void (*)(volatile unsigned char *))(unsigned long)callback)(
                object);                                    /* 0x30690 */
            if (recovered_locomotion_ldos(object, 0x172U) == 0U) {
                f176 = recovered_locomotion_ldos(object, 0x176U);
                if (f174 == 1U)
                    cfg_lo = (f176 == 0U)
                        ? recovered_locomotion_cfg_u32(cfg, 0x5ecU)
                        : (f176 == 1U
                               ? recovered_locomotion_cfg_u32(cfg, 0x5f0U)
                               : recovered_locomotion_cfg_u32(cfg, 0x5e8U));
                else if (f174 == 2U)
                    cfg_lo = (f176 == 0U)
                        ? recovered_locomotion_cfg_u32(cfg, 0x5f8U)
                        : (f176 == 1U
                               ? recovered_locomotion_cfg_u32(cfg, 0x5fcU)
                               : recovered_locomotion_cfg_u32(cfg, 0x5f4U));
                else
                    cfg_lo = (f176 == 0U)
                        ? recovered_locomotion_cfg_u32(cfg, 0x604U)
                        : (f176 == 1U
                               ? recovered_locomotion_cfg_u32(cfg, 0x608U)
                               : recovered_locomotion_cfg_u32(cfg, 0x600U));
                *(volatile u16 *)(object + 0x18e) = (u16)cfg_lo;
            }
            recovered_locomotion_state31_commit(object, cfg);
            return;
        }
    }

    /* 0x307e8: +0x170 = 0. */
    *(volatile u16 *)(object + 0x170) = 0U;

    /* 0x307ec-0x308b4: publish the cfg word pair selected by +0x17e.  The
     * +0x176 index is shifted left 5 by the shlo 16 / shri 11 pair. */
    v17e = recovered_locomotion_ldos(object, 0x17eU);
    f176 = recovered_locomotion_ldos(object, 0x176U);
    if (v17e <= 3U) {
        if (v17e == 0U) {
            cfg_hi = recovered_locomotion_cfg_u32(cfg, 0xf8U + (f176 << 5));
            cfg_lo = recovered_locomotion_cfg_u32(cfg, 0xfcU + (f176 << 5));
        } else {
            cfg_hi = recovered_locomotion_cfg_u32(cfg, 0x100U + (f176 << 5));
            cfg_lo = recovered_locomotion_cfg_u32(cfg, 0x104U + (f176 << 5));
        }
        recovered_locomotion_publish_hi = cfg_hi;           /* 0x51ab0c */
        recovered_locomotion_publish_lo = cfg_lo;           /* 0x51ab08 */
    } else if (v17e == 4U) {
        cfg_hi = recovered_locomotion_cfg_u32(cfg, 0x108U + (f176 << 5));
        cfg_lo = recovered_locomotion_cfg_u32(cfg, 0x10cU + (f176 << 5));
        recovered_locomotion_publish_hi = cfg_hi;           /* 0x51ab0c */
        recovered_locomotion_publish_lo = cfg_lo;           /* 0x51ab08 */
    }

    /* 0x308b8-0x308e4: +0x17a += 1, then the +0x30000 < +0x17e<<16 gate. */
    old17a = recovered_locomotion_ldos(object, 0x17aU);
    *(volatile u16 *)(object + 0x17a) = (u16)(old17a + 1U);
    recovered_locomotion_counter_b = (u16)old17a;           /* 0x51ab12 */
    recovered_locomotion_counter_a = (u16)old17a;           /* 0x51ab10 */
    v17e = recovered_locomotion_ldos(object, 0x17eU);
    if (!((s32)(v17e << 16) > (s32)0x30000U)) {
        if (recovered_locomotion_weapon_gate(object, &selector)) {
            *(volatile u16 *)(object + 0x174) = (u16)selector;
            /* 0x30938-0x3094c: the selector-2 arm clears +0x17a when +0x17e
             * is a non-negative nonzero value (cmpibge 0,g4). */
            if (selector == 2U && v17e != 0U && (v17e & 0x8000U) == 0U)
                *(volatile u16 *)(object + 0x17a) = 0U;
        }
    }

    /* 0x30964-0x30984: ldis 0x51ab10,g5; cmpibl g5,(count-1) is false for any
     * real 16-bit count, but the listing's guard is kept. */
    record = recovered_locomotion_publish_lo;               /* 0x51ab08 */
    if ((s32)0x51ab10U < (s32)
            ((u32)recovered_locomotion_ldos(
                 (const volatile unsigned char *)(unsigned long)record, 0x4U)
             - 1U)) {
        recovered_locomotion_state31_commit(object, cfg);
        return;
    }

    /* 0x30988-0x309b0: republish the count-1 and branch on +0x17e >= 3. */
    recovered_locomotion_counter_a = (u16)
        ((u32)recovered_locomotion_ldos(
             (const volatile unsigned char *)(unsigned long)record, 0x4U)
         - 1U);
    recovered_locomotion_counter_b = recovered_locomotion_counter_a;
    v17e = recovered_locomotion_ldos(object, 0x17eU);

    if ((s32)(v17e << 16) > (s32)0x20000U) {
        if (v17e == 3U) {
            /* 0x309c8-0x30a64: classify +0x102 and compare +0x188. */
            u32 p102 = recovered_locomotion_ldos(object, 0x102U);
            u32 state33 = 0U;

            if (p102 != 0x8000U) {
                u32 p188 = recovered_locomotion_ldos(object, 0x188U);
                u32 cls = (p102 + 0xefffU) & 0xffffU;

                if (0xfffU < cls) {                          /* cmpo 0xfff,g4 */
                    cls = (p102 + 0xdfffU) & 0xffffU;
                    if (cls > 0x3ffeU) {                     /* cmpobg g4,0x3ffe */
                        cls = (p102 + 0xa000U) & 0xffffU;
                        cls = (0xfffU < cls) ? 0U : 3U;
                    } else {
                        cls = 1U;
                    }
                } else {
                    cls = 2U;
                }
                if (p188 == cls)
                    state33 = 1U;
            }

            if (state33 != 0U) {
                *(volatile u16 *)(object + 0x172) = (u16)(31U + 2U);
                *(volatile u16 *)(object + 0x170) = 1U;
                *(volatile u16 *)(object + 0x178) = 0U;
                *(volatile u16 *)(object + 0x17a) = 0U;
            } else if (recovered_locomotion_ldos(object, 0x174U) == 16U) {
                recovered_locomotion_state35_commit(object);
            } else {
                recovered_locomotion_advance_clip(object);
            }
        } else if (v17e == 4U) {
            /* 0x30a9c-0x30ac0: state 31 -> 0 sub-phase, +0x1c4 = 0. */
            *(volatile u16 *)(object + 0x172) = 0U;
            *(volatile u16 *)(object + 0x170) = 1U;
            *(volatile u16 *)(object + 0x194) = 0U;
            *(volatile u16 *)(object + 0x178) = 0U;
            *(volatile u16 *)(object + 0x17a) = 0U;
            *(volatile u32 *)(object + 0x1c4) = 0U;
            *(volatile u8 *)(object + 0x1a8) = 2U;
        } else {
            recovered_locomotion_advance_clip(object);
        }
    } else if (recovered_locomotion_ldos(object, 0x174U) == 16U) {
        recovered_locomotion_state35_commit(object);
    } else {
        recovered_locomotion_advance_clip(object);
    }

    recovered_locomotion_state31_commit(object, cfg);
}

void recovered_locomotion_state_34_run(volatile unsigned char *object)
{
    volatile unsigned char *cfg;
    u32 f176;
    u32 index;
    u32 g6;
    u32 g5;
    u32 g4;
    u32 selector;
    u32 record;
    u32 count;
    u32 old17a;

    cfg = recovered_locomotion_config(object);

    /* 0x30e50: +0x170 = 0. */
    *(volatile u16 *)(object + 0x170) = 0U;

    /* 0x30e54-0x30e84: lda (g4)[g4*2] makes the +0x176 index 3*+0x176; the
     * cfg+0x180/0x184 loads then scale it by 8 (index * 8 bytes). */
    f176 = recovered_locomotion_ldos(object, 0x176U);
    index = (f176 + (f176 << 1)) << 3;
    g6 = recovered_locomotion_cfg_u32(cfg, 0x180U + index);

    f176 = recovered_locomotion_ldos(object, 0x176U);
    index = (f176 + (f176 << 1)) << 3;
    g5 = recovered_locomotion_cfg_u32(cfg, 0x184U + index);

    /* 0x30e8c-0x30ea0: cmpi g4,0; bne; publish the pair. */
    f176 = recovered_locomotion_ldos(object, 0x176U);
    recovered_locomotion_publish_hi = g6;                   /* 0x51ab0c */
    recovered_locomotion_publish_lo = g5;                   /* 0x51ab08 */

    /* 0x30ea4-0x30ec4: +0x1c4 from the cfg+0x570/0x574/0x56c triplet. */
    if (f176 == 0U)
        g4 = recovered_locomotion_cfg_u32(cfg, 0x570U);
    else if (f176 == 1U)
        g4 = recovered_locomotion_cfg_u32(cfg, 0x574U);
    else
        g4 = recovered_locomotion_cfg_u32(cfg, 0x56cU);
    *(volatile u32 *)(object + 0x1c4) = g4;

    /* 0x30ec8-0x30f2c: the shared weapon sentinel gate. */
    if (recovered_locomotion_weapon_gate(object, &selector))
        *(volatile u16 *)(object + 0x174) = (u16)selector;

    /* 0x30f30-0x30f54: clip scan of the published record count. */
    record = recovered_locomotion_publish_lo;               /* 0x51ab08 */
    old17a = recovered_locomotion_ldos(object, 0x17aU);
    count = (u32)recovered_locomotion_ldos(
        (const volatile unsigned char *)(unsigned long)record, 0x4U);
    if ((s32)old17a < (s32)(count - 1U)) {
        /* 0x30fcc-0x30fe8: +0x17a += 1. */
        u32 current = recovered_locomotion_ldos(object, 0x17aU);

        recovered_locomotion_counter_a = (u16)current;      /* 0x51ab10 */
        *(volatile u16 *)(object + 0x17a) = (u16)(current + 1U);
        recovered_locomotion_counter_b = (u16)current;      /* 0x51ab12 */
        return;
    }

    /* 0x30f58-0x30f90: clip end -> state 31 (+0x172 = 31). */
    count = (u32)recovered_locomotion_ldos(
        (const volatile unsigned char *)(unsigned long)record, 0x4U);
    *(volatile u16 *)(object + 0x172) = (u16)31U;
    *(volatile u16 *)(object + 0x170) = 0U;
    *(volatile u16 *)(object + 0x17a) = 0U;
    *(volatile u16 *)(object + 0x17e) = 1U;
    *(volatile u16 *)(object + 0x1a0) = 0U;
    recovered_locomotion_counter_a = (u16)(count - 1U);     /* 0x51ab10 */
    recovered_locomotion_counter_b = (u16)(count - 1U);     /* 0x51ab12 */
    *(volatile u8 *)(object + 0x1a8) = 1U;
    *(volatile u8 *)(object + 0x1a9) = 1U;

    /* 0x30f94-0x30fc8: +0x4e += cfg+0x658 while below cfg+0x660. */
    cfg = recovered_locomotion_config(object);
    g4 = (u32)recovered_locomotion_ldos(object, 0x4eU);
    g5 = recovered_locomotion_cfg_u32(cfg, 0x658U);
    g6 = recovered_locomotion_cfg_u32(cfg, 0x660U);
    if (!((s32)(g4 + g5) >= (s32)g6)) {                     /* cmpibge g4,g6 */
        g4 = recovered_locomotion_cfg_u32(cfg, 0x658U);
        g5 = (u32)recovered_locomotion_ldos(object, 0x4eU);
        *(volatile u16 *)(object + 0x4e) = (u16)(g4 + g5);
    }
}
