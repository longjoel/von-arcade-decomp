/*
 * Bounded freestanding runnable recovered-C unit for the i960 input-facing
 * locomotion/idle object state handlers 0, 1, 15, 16, 17, 32 and 36.
 *
 * Listing spans in von/build/disasm/vonj-maincpu.lst:
 *    0  0x2f580-0x2f92c    1  0x2f930-0x2fa14   15 0x2fa20-0x2fb10
 *   16 0x2fb20-0x2fd40    17 0x2fd50-0x2fe24   32 0x30c20-0x30d38
 *   36 0x31210-0x313d4
 *
 * The 43-entry 0x32560 update table keys these on object+0x172 (16-byte
 * stride): 0x32560 -> 0x2f580 (state 0), 0x32570 -> 0x2f930 (state 1),
 * 0x32650 -> 0x2fa20 (state 15), 0x32660 -> 0x2fb20 (state 16),
 * 0x32670 -> 0x2fd50 (state 17), 0x32760 -> 0x30c20 (state 32) and
 * 0x327a0 -> 0x31210 (state 36).  The 0x72ea0 commit gate accepts a command
 * only in +0x172 in {15,16,31}; this slice is the input-facing set.
 *
 * Config pointer
 *   st g6,0x6c(g0) at 0x27558 seeds object+0x6c.  The listing reaches the same
 *   block through the absolute slot 0x51ab14; this unit reads object+0x6c so it
 *   stays freestanding and host-testable.  The absolute publication cells
 *   0x51ab08/0x51ab0c (record-pointer scratch) and 0x51ab10/0x51ab12
 *   (write-only counters) are file-static stand-ins.
 *
 * Projection / callbacks
 *   The cfg callback slots (state 0 0x3a8/0x3b0/0x3c0/0x3b8, state 1 0x3c8,
 *   state 16 0x3ac/0x3b4/0x3c4/0x3bc) are external.  The 0x32810 per-object
 *   prefix (recovered_object_update_prefix_32810.c) caches the opcode-31
 *   projection response at object+0x7c and the opcode-10 response at object+0x84
 *   (the 0x6f6f0 projection result lands there); a callback that needs the
 *   projection reads those two cached words instead of the live 0x884000
 *   exchange.  None of these seven slices calls 0x6f6f0 directly.  Where the
 *   listing guards a slot with cmpibe 0,g4 the callback is invoked only when
 *   non-zero; state 1's cfg+0x3c8 call (0x2f940/0x2f948) has no cmpibe in the
 *   listing and is guarded here so the bounded unit stays runnable on a zero
 *   slot.
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef short s16;
typedef int s32;

/* 0x27558/0x2f934/0x2fc6c: the config pointer lives at object+0x6c. */
#define RECOVERED_STATE_LOCOMOTION_CONFIG_OFFSET 0x6cU

/* 0x51ab08/0x51ab0c/0x51ab10/0x51ab12: absolute scratch stand-ins. */
static volatile u32 recovered_state_locomotion_publish_lo;  /* 0x51ab08 */
static volatile u32 recovered_state_locomotion_publish_hi;  /* 0x51ab0c */
static volatile u16 recovered_state_locomotion_counter_a;   /* 0x51ab10 */
static volatile u16 recovered_state_locomotion_counter_b;   /* 0x51ab12 */

static volatile unsigned char *recovered_state_locomotion_config(
    volatile unsigned char *object)
{
    return (volatile unsigned char *)(unsigned long)
        *(volatile u32 *)(object + RECOVERED_STATE_LOCOMOTION_CONFIG_OFFSET);
}

static u16 recovered_state_locomotion_ld16(const volatile unsigned char *object,
                                           u32 offset)
{
    return *(const volatile u16 *)(object + offset);
}

static u8 recovered_state_locomotion_ld8(const volatile unsigned char *object,
                                         u32 offset)
{
    return *(const volatile u8 *)(object + offset);
}

static void recovered_state_locomotion_st32(volatile unsigned char *object,
                                            u32 offset, u32 value)
{
    *(volatile u32 *)(object + offset) = value;
}

static void recovered_state_locomotion_st16(volatile unsigned char *object,
                                            u32 offset, u32 value)
{
    *(volatile u16 *)(object + offset) = (u16)value;
}

static void recovered_state_locomotion_st8(volatile unsigned char *object,
                                           u32 offset, u32 value)
{
    *(volatile u8 *)(object + offset) = (u8)value;
}

static u32 recovered_state_locomotion_cfg_u32(const volatile unsigned char *cfg,
                                              u32 offset)
{
    return *(const volatile u32 *)(cfg + offset);
}

/* shlo 16 / shri 16 pairs: sign-extend the low 16 bits to a full word. */
static s32 recovered_state_locomotion_sx16(u32 value)
{
    return (s32)(s16)(u16)value;
}

static u32 recovered_state_locomotion_clip_count(
    const volatile unsigned char *record)
{
    return (u32)recovered_state_locomotion_ld16(record, 0x4U);
}

/*
 * 0x2f940-0x2f948 (state 1) and the cfg callbacks at 0x2f5d4/0x2f5f8/0x2f61c/
 * 0x2f640 (state 0) and 0x2fb44/0x2fb78/0x2fbac/0x2fc18 (state 16).  The slot
 * is external; a non-zero pointer is invoked with the object, and the cached
 * projection words at object+0x7c/+0x84 are the callback input boundary.
 */
static int recovered_state_locomotion_cfg_invoke(
    volatile unsigned char *object, u32 callback)
{
    if (callback == 0U)
        return 0;
    ((void (*)(volatile unsigned char *))(unsigned long)callback)(object);
    return 1;
}

/*
 * 0x2f588-0x2f5b0 (state 0): delta = (s16)(+0x34 + +0x184 - +0x2e);
 * +0x2e += delta >> 1 (shlo 16 / shri 16 sign-extend, shrdi 1 halving).
 */
static void recovered_state_locomotion_facing_slew(
    volatile unsigned char *object)
{
    u32 current = (u32)recovered_state_locomotion_ld16(object, 0x2eU);
    u32 raw = (u32)recovered_state_locomotion_ld16(object, 0x34U)
            + (u32)recovered_state_locomotion_ld16(object, 0x184U) - current;
    s32 delta = recovered_state_locomotion_sx16(raw);

    delta >>= 1;
    recovered_state_locomotion_st16(object, 0x2eU, current + (u32)delta);
}

/*
 * 0x312b0-0x31314 (state 36): the +0x138/+0x139/+0x13a/+0x13c weapon
 * sentinels.  Each arm needs its +0x13x byte at 0xff and bit 0 of the matching
 * +0x1d_x companion; the fall-through +0x13c byte selects 16.  Returns 1 and
 * the +0x174 selector when an arm fires.
 */
static u32 recovered_state_locomotion_weapon_gate(
    const volatile unsigned char *object, u32 *selector)
{
    if (recovered_state_locomotion_ld8(object, 0x13aU) == 0xffU
            && (recovered_state_locomotion_ld8(object, 0x1dfU) & 1U) != 0U) {
        *selector = 3U;
        return 1U;
    }
    if (recovered_state_locomotion_ld8(object, 0x138U) == 0xffU
            && (recovered_state_locomotion_ld8(object, 0x1deU) & 1U) != 0U) {
        *selector = 1U;
        return 1U;
    }
    if (recovered_state_locomotion_ld8(object, 0x139U) == 0xffU
            && (recovered_state_locomotion_ld8(object, 0x1ddU) & 1U) != 0U) {
        *selector = 2U;
        return 1U;
    }
    if (recovered_state_locomotion_ld8(object, 0x13cU) == 0xffU) {
        *selector = 16U;
        return 1U;
    }
    return 0U;
}

/*
 * 0x2f9a0-0x2fa10 (state 1): classify +0x102 into +0x188.
 *   cls = (i + 0xefff) & 0xffff;
 *   if (0xfff < cls) { cls = (i + 0xdfff) & 0xffff;
 *       if (cls > 0x3ffe) cls = (0xfff < ((i + 0xa000) & 0xffff)) ? 0 : 3;
 *       else cls = 1; }
 *   else cls = 2;
 * The same shape is used by the state-31 classifier (0x309c8-0x30a64).
 */
static u32 recovered_state_locomotion_classify(u32 word)
{
    u32 cls = (word + 0xefffU) & 0xffffU;

    if (0xfffU < cls) {
        cls = (word + 0xdfffU) & 0xffffU;
        if (cls > 0x3ffeU)
            cls = (0xfffU < ((word + 0xa000U) & 0xffffU)) ? 0U : 3U;
        else
            cls = 1U;
    } else {
        cls = 2U;
    }
    return cls;
}

/* 0x2f788-0x2f7bc (state 0): cfg+0x9c -> 0x51ab08, cfg+0x98 -> 0x51ab0c. */
static void recovered_state_locomotion_0_publish_98(
    volatile unsigned char *object, const volatile unsigned char *cfg)
{
    u32 v194 = (u32)recovered_state_locomotion_ld16(object, 0x194U);

    recovered_state_locomotion_publish_lo =
        recovered_state_locomotion_cfg_u32(cfg, 0x9cU);      /* 0x51ab08 */
    recovered_state_locomotion_publish_hi =
        recovered_state_locomotion_cfg_u32(cfg, 0x98U);      /* 0x51ab0c */
    recovered_state_locomotion_counter_b = (u16)v194;        /* 0x51ab12 */
    recovered_state_locomotion_counter_a = (u16)v194;        /* 0x51ab10 */
    recovered_state_locomotion_st16(object, 0x1b2U, 0U);
}

/* 0x2f6c8-0x2f6e8 and 0x2f764-0x2f784 (state 0): cfg+0xac -> 0x51ab08,
 * cfg+0xa8 -> 0x51ab0c with the negated +0x194 counters. */
static void recovered_state_locomotion_0_publish_ac(
    volatile unsigned char *object, const volatile unsigned char *cfg)
{
    u32 v194 = (u32)recovered_state_locomotion_ld16(object, 0x194U);

    recovered_state_locomotion_publish_lo =
        recovered_state_locomotion_cfg_u32(cfg, 0xacU);      /* 0x51ab08 */
    recovered_state_locomotion_publish_hi =
        recovered_state_locomotion_cfg_u32(cfg, 0xa8U);      /* 0x51ab0c */
    recovered_state_locomotion_counter_b = (u16)(0U - v194); /* 0x51ab12 */
    recovered_state_locomotion_counter_a = (u16)(0U - v194); /* 0x51ab10 */
    recovered_state_locomotion_st16(object, 0x1b2U, 0U);
}

/* 0x2f658-0x2f6c0 (state 0): +0x194 ramp when +0x10e is 1..0x7fff. */
static void recovered_state_locomotion_0_ramp_positive(
    volatile unsigned char *object)
{
    s32 v = recovered_state_locomotion_sx16(
        (u32)recovered_state_locomotion_ld16(object, 0x194U));

    if (v < -15) {
        v = -15;
    } else if (v < -1) {
        v = v + 2;
    } else {
        u32 raw = (u32)recovered_state_locomotion_ld16(object, 0x194U);
        s32 g4 = (s32)(raw << 16);
        s32 g2 = (s32)(7U << 17);                           /* shlo 17,7 */

        if (g4 > g2)
            v = 15;
        else
            v = v + 1;
    }
    recovered_state_locomotion_st16(object, 0x194U, (u16)v);
}

/* 0x2f6f4-0x2f758 (state 0): +0x194 ramp when +0x10e has bit 15 set. */
static void recovered_state_locomotion_0_ramp_negative(
    volatile unsigned char *object)
{
    u32 raw = (u32)recovered_state_locomotion_ld16(object, 0x194U);
    s32 v;

    if ((s32)(raw << 16) <= (s32)(15U << 16)) {
        if ((s32)(raw << 16) <= (s32)(1U << 16)) {          /* setbit 16,0 */
            if (recovered_state_locomotion_sx16(raw) <= -15)
                v = -15;
            else
                v = (s32)raw - 1;
        } else {
            v = (s32)raw - 2;
        }
    } else {
        v = 15;
    }
    recovered_state_locomotion_st16(object, 0x194U, (u16)v);
}

/*
 * 0x2f8a4-0x2f924 (state 0): +0x10e == 0 and +0x194 == 0.  Publish
 * cfg+0x70/0x74, reset +0x17a at the clip end, then bump +0x17a only while
 * +0x1db <= 0xf9 and (+0x1dc & 0xff) <= 0xf9.
 */
static void recovered_state_locomotion_0_hold_phase(
    volatile unsigned char *object, const volatile unsigned char *cfg)
{
    volatile unsigned char *record = (volatile unsigned char *)(unsigned long)
        recovered_state_locomotion_cfg_u32(cfg, 0x74U);
    u32 count = recovered_state_locomotion_clip_count(record);
    u32 f17a = (u32)recovered_state_locomotion_ld16(object, 0x17aU);

    recovered_state_locomotion_publish_hi =
        recovered_state_locomotion_cfg_u32(cfg, 0x70U);      /* 0x51ab0c */
    recovered_state_locomotion_publish_lo = (u32)(unsigned long)record;
                                                             /* 0x51ab08 */
    if (!(recovered_state_locomotion_sx16(f17a)
              < recovered_state_locomotion_sx16(count)))
        recovered_state_locomotion_st16(object, 0x17aU, 0U);

    f17a = (u32)recovered_state_locomotion_ld16(object, 0x17aU);
    recovered_state_locomotion_counter_a = (u16)f17a;        /* 0x51ab10 */
    recovered_state_locomotion_counter_b = (u16)f17a;        /* 0x51ab12 */

    if ((u32)recovered_state_locomotion_ld8(object, 0x1dbU) > 0xf9U
            || ((u32)recovered_state_locomotion_ld8(object, 0x1dcU) & 0xffU)
                   > 0xf9U) {
        recovered_state_locomotion_st16(object, 0x1b2U, 0U);
        return;
    }
    recovered_state_locomotion_st16(object, 0x17aU, f17a + 1U);
    recovered_state_locomotion_st16(object, 0x1b2U, 0U);
}

/* 0x2f7c0 (state 0): +0x10e == 0 phase. */
static void recovered_state_locomotion_0_zero_phase(
    volatile unsigned char *object, const volatile unsigned char *cfg)
{
    u32 v194 = (u32)recovered_state_locomotion_ld16(object, 0x194U);

    if ((s32)(v194 << 16) <= 0) {
        if ((v194 & 0x8000U) == 0U) {
            recovered_state_locomotion_0_hold_phase(object, cfg);
            return;
        }
        /* 0x2f834-0x2f89c: +0x194 negative, +0x194 += 1, cfg+0xb0/0xb4. */
        {
            volatile unsigned char *record =
                (volatile unsigned char *)(unsigned long)
                    recovered_state_locomotion_cfg_u32(cfg, 0xb4U);
            u32 newv = (u32)recovered_state_locomotion_ld16(object, 0x194U)
                     + 1U;
            u32 count = recovered_state_locomotion_clip_count(record);
            u32 sum = count + newv - 1U;

            recovered_state_locomotion_st16(object, 0x194U, newv);
            recovered_state_locomotion_publish_hi =
                recovered_state_locomotion_cfg_u32(cfg, 0xb0U);
            recovered_state_locomotion_publish_lo =
                (u32)(unsigned long)record;
            recovered_state_locomotion_counter_a = (u16)sum;
            recovered_state_locomotion_counter_b = (u16)sum;
            if (recovered_state_locomotion_sx16(sum) < 0) {
                recovered_state_locomotion_counter_a = 0U;
                recovered_state_locomotion_counter_b = 0U;
            }
            recovered_state_locomotion_st16(object, 0x1b2U, 0U);
        }
        return;
    }

    /* 0x2f7cc-0x2f828: +0x194 positive, +0x194 -= 1, cfg+0xa0/0xa4. */
    {
        volatile unsigned char *record = (volatile unsigned char *)(unsigned long)
            recovered_state_locomotion_cfg_u32(cfg, 0xa4U);
        u32 newv = (u32)recovered_state_locomotion_ld16(object, 0x194U) - 1U;
        u32 count = recovered_state_locomotion_clip_count(record);
        u32 remain = (u32)(u16)(count - (newv + 1U));

        recovered_state_locomotion_st16(object, 0x194U, newv);
        recovered_state_locomotion_publish_hi =
            recovered_state_locomotion_cfg_u32(cfg, 0xa0U);
        recovered_state_locomotion_publish_lo = (u32)(unsigned long)record;
        recovered_state_locomotion_counter_a = (u16)remain;
        recovered_state_locomotion_counter_b = (u16)remain;
        if (recovered_state_locomotion_sx16(remain) < 0) {
            recovered_state_locomotion_counter_a = 0U;
            recovered_state_locomotion_counter_b = 0U;
        }
        recovered_state_locomotion_st16(object, 0x1b2U, 0U);
    }
}

/*
 * State 0 (0x2f580).  Idle stand clip: +0x186/+0x188 cleared, the facing
 * half-slew into +0x2e, the +0x170 2/3/4/5 callback dispatch, then the
 * +0x10e / +0x194 phase machine that republishes cfg+0x70/0x74, 0x98/0x9c,
 * 0xa0/0xa4, 0xa8/0xac or 0xb0/0xb4 and gates +0x17a.  +0x2e is the only
 * object counter advanced; +0x1c4 and +0x172 are not written.
 */
void recovered_state_locomotion_0_run(volatile unsigned char *object)
{
    volatile unsigned char *cfg;
    u32 v170;
    u32 f10e;
    u32 v194;

    cfg = recovered_state_locomotion_config(object);

    /* 0x2f580/0x2f584: +0x186 = +0x188 = 0. */
    recovered_state_locomotion_st16(object, 0x186U, 0U);
    recovered_state_locomotion_st16(object, 0x188U, 0U);

    /* 0x2f588-0x2f5b0: facing half-slew into +0x2e. */
    recovered_state_locomotion_facing_slew(object);

    /* 0x2f5b4-0x2f648: +0x170 dispatch.  A non-zero callback runs and leaves
     * through 0x2f928 (+0x1b2 = 0). */
    v170 = (u32)recovered_state_locomotion_ld16(object, 0x170U);
    if (v170 == 2U
            && recovered_state_locomotion_cfg_invoke(
                   object, recovered_state_locomotion_cfg_u32(cfg, 0x3a8U))) {
        recovered_state_locomotion_st16(object, 0x1b2U, 0U);
        return;
    }
    if (v170 == 3U
            && recovered_state_locomotion_cfg_invoke(
                   object, recovered_state_locomotion_cfg_u32(cfg, 0x3b0U))) {
        recovered_state_locomotion_st16(object, 0x1b2U, 0U);
        return;
    }
    if (v170 == 4U
            && recovered_state_locomotion_cfg_invoke(
                   object, recovered_state_locomotion_cfg_u32(cfg, 0x3c0U))) {
        recovered_state_locomotion_st16(object, 0x1b2U, 0U);
        return;
    }
    if (v170 == 5U
            && recovered_state_locomotion_cfg_invoke(
                   object, recovered_state_locomotion_cfg_u32(cfg, 0x3b8U))) {
        recovered_state_locomotion_st16(object, 0x1b2U, 0U);
        return;
    }

    /* 0x2f64c: +0x10e bit 15 set or zero goes to 0x2f6ec; 1..0x7fff ramps. */
    f10e = (u32)recovered_state_locomotion_ld16(object, 0x10eU);
    if ((s32)(f10e << 16) <= 0) {
        if ((f10e & 0x8000U) == 0U) {
            recovered_state_locomotion_0_zero_phase(object, cfg);
            return;
        }
        recovered_state_locomotion_0_ramp_negative(object);
        v194 = (u32)recovered_state_locomotion_ld16(object, 0x194U);
        if ((s32)(v194 << 16) > 0)
            recovered_state_locomotion_0_publish_98(object, cfg);
        else
            recovered_state_locomotion_0_publish_ac(object, cfg);
        return;
    }

    recovered_state_locomotion_0_ramp_positive(object);
    v194 = (u32)recovered_state_locomotion_ld16(object, 0x194U);
    if ((v194 & 0x8000U) != 0U)
        recovered_state_locomotion_0_publish_ac(object, cfg);
    else
        recovered_state_locomotion_0_publish_98(object, cfg);
}

/*
 * State 1 (0x2f930).  Action-class recovery: the cfg+0x3c8 callback runs,
 * then +0x17c == 0xffff selects +0x172 = 0 (or 15 when +0x139 == 0 and
 * +0x102 bit 15 is clear).  +0x102 is copied to +0x186 and its class to
 * +0x188; +0x1b2 and +0x1c4 are not written.
 */
void recovered_state_locomotion_1_run(volatile unsigned char *object)
{
    volatile unsigned char *cfg = recovered_state_locomotion_config(object);
    u32 word;

    /* 0x2f938/0x2f93c: +0x186 = +0x188 = 0. */
    recovered_state_locomotion_st16(object, 0x186U, 0U);
    recovered_state_locomotion_st16(object, 0x188U, 0U);

    /* 0x2f940-0x2f948: cfg+0x3c8 callback (unconditional in the listing). */
    recovered_state_locomotion_cfg_invoke(
        object, recovered_state_locomotion_cfg_u32(cfg, 0x3c8U));

    /* 0x2f94c-0x2f964: only +0x17c == 0xffff (-1) continues. */
    if ((u16)recovered_state_locomotion_ld16(object, 0x17cU) != 0xffffU)
        return;

    /* 0x2f968-0x2f97c. */
    recovered_state_locomotion_st16(object, 0x172U, 0U);
    recovered_state_locomotion_st16(object, 0x170U, 1U);
    recovered_state_locomotion_st16(object, 0x194U, 0U);
    recovered_state_locomotion_st16(object, 0x178U, 0U);
    recovered_state_locomotion_st16(object, 0x17aU, 0U);

    /* 0x2f980: +0x139 != 0 returns with +0x172 = 0. */
    if (recovered_state_locomotion_ld8(object, 0x139U) != 0U)
        return;

    /* 0x2f988: +0x102 bit 15 returns with +0x172 = 0. */
    word = (u32)recovered_state_locomotion_ld16(object, 0x102U);
    if ((word & 0x8000U) != 0U)
        return;

    /* 0x2f990/0x2f994: +0x172 = 15, +0x170 = 1. */
    recovered_state_locomotion_st16(object, 0x172U, 15U);
    recovered_state_locomotion_st16(object, 0x170U, 1U);

    /* 0x2f9a0-0x2fa10: +0x186 = +0x102, +0x188 = class, +0x178/+0x17a = 0. */
    recovered_state_locomotion_st16(object, 0x186U, word);
    recovered_state_locomotion_st16(object, 0x188U,
                                    recovered_state_locomotion_classify(word));
    recovered_state_locomotion_st16(object, 0x178U, 0U);
    recovered_state_locomotion_st16(object, 0x17aU, 0U);
}

/*
 * State 15 (0x2fa20).  Locomotion clip player keyed by +0x188: publish
 * cfg+0x78/0x7c (+0x188 * 8), advance +0x17a, and on clip end set +0x172 = 16
 * and zero +0x178/+0x17a.  +0x1c4 is cfg+0x534 (+0x188 == 0), cfg+0x538
 * (+0x188 == 1) or cfg+0x530; +0x1b2 = 0.
 */
void recovered_state_locomotion_15_run(volatile unsigned char *object)
{
    volatile unsigned char *cfg = recovered_state_locomotion_config(object);
    u32 f188 = (u32)recovered_state_locomotion_ld16(object, 0x188U);
    u32 index = f188 << 3;
    volatile unsigned char *record = (volatile unsigned char *)(unsigned long)
        recovered_state_locomotion_cfg_u32(cfg, 0x7cU + index);
    u32 count = recovered_state_locomotion_clip_count(record);
    u32 f17a = (u32)recovered_state_locomotion_ld16(object, 0x17aU);
    u32 speed;

    recovered_state_locomotion_publish_lo = (u32)(unsigned long)record;
                                                             /* 0x51ab08 */
    recovered_state_locomotion_publish_hi =
        recovered_state_locomotion_cfg_u32(cfg, 0x78U + index);
                                                             /* 0x51ab0c */

    if (recovered_state_locomotion_sx16(f17a)
            < recovered_state_locomotion_sx16(count) - 1) {
        /* 0x2fab8-0x2facc: +0x17a += 1. */
        recovered_state_locomotion_st16(object, 0x17aU, f17a + 1U);
        recovered_state_locomotion_counter_a = (u16)f17a;    /* 0x51ab10 */
        recovered_state_locomotion_counter_b = (u16)f17a;    /* 0x51ab12 */
    } else {
        /* 0x2fa94-0x2faac: clip end -> +0x172 = 16. */
        recovered_state_locomotion_st16(object, 0x172U, 16U);
        recovered_state_locomotion_st16(object, 0x178U, 0U);
        recovered_state_locomotion_st16(object, 0x17aU, 0U);
        recovered_state_locomotion_counter_a = (u16)(count - 1U);
        recovered_state_locomotion_counter_b = (u16)(count - 1U);
    }

    /* 0x2fad4-0x2fb04: +0x1c4 by +0x188. */
    if (f188 == 0U)
        speed = recovered_state_locomotion_cfg_u32(cfg, 0x534U);
    else if (f188 == 1U)
        speed = recovered_state_locomotion_cfg_u32(cfg, 0x538U);
    else
        speed = recovered_state_locomotion_cfg_u32(cfg, 0x530U);
    recovered_state_locomotion_st32(object, 0x1c4U, speed);

    /* 0x2fb08. */
    recovered_state_locomotion_st16(object, 0x1b2U, 0U);
}

/*
 * State 16 (0x2fb20).  Movement clip: +0x170 2/3/4/5 dispatch to
 * cfg+0x3ac/0x3b4/0x3c4/0x3bc, each followed by a +0x188 speed selection from
 * cfg+0x554..0x568.  When no callback fires the default clip publishes
 * cfg+0xb8/0xbc (+0x188 * 8), advances or resets +0x17a and selects +0x1c4
 * from cfg+0x53c/0x540/0x544.  +0x1b2 = 0; +0x172 is not written.
 */
void recovered_state_locomotion_16_run(volatile unsigned char *object)
{
    volatile unsigned char *cfg = recovered_state_locomotion_config(object);
    u32 v170 = (u32)recovered_state_locomotion_ld16(object, 0x170U);
    u32 f188;

    if (v170 == 2U
            && recovered_state_locomotion_cfg_invoke(
                   object, recovered_state_locomotion_cfg_u32(cfg, 0x3acU))) {
        f188 = (u32)recovered_state_locomotion_ld16(object, 0x188U);
        if (f188 == 0U)
            recovered_state_locomotion_st32(object, 0x1c4U,
                recovered_state_locomotion_cfg_u32(cfg, 0x558U));
        else if (f188 == 1U)
            recovered_state_locomotion_st32(object, 0x1c4U,
                recovered_state_locomotion_cfg_u32(cfg, 0x55cU));
        else
            recovered_state_locomotion_st32(object, 0x1c4U,
                recovered_state_locomotion_cfg_u32(cfg, 0x554U));
        recovered_state_locomotion_st16(object, 0x1b2U, 0U);
        return;
    }
    if (v170 == 3U
            && recovered_state_locomotion_cfg_invoke(
                   object, recovered_state_locomotion_cfg_u32(cfg, 0x3b4U))) {
        f188 = (u32)recovered_state_locomotion_ld16(object, 0x188U);
        if (f188 == 0U)
            recovered_state_locomotion_st32(object, 0x1c4U,
                recovered_state_locomotion_cfg_u32(cfg, 0x564U));
        else if (f188 == 1U)
            recovered_state_locomotion_st32(object, 0x1c4U,
                recovered_state_locomotion_cfg_u32(cfg, 0x568U));
        else
            recovered_state_locomotion_st32(object, 0x1c4U,
                recovered_state_locomotion_cfg_u32(cfg, 0x560U));
        recovered_state_locomotion_st16(object, 0x1b2U, 0U);
        return;
    }
    if (v170 == 4U
            && recovered_state_locomotion_cfg_invoke(
                   object, recovered_state_locomotion_cfg_u32(cfg, 0x3c4U))) {
        f188 = (u32)recovered_state_locomotion_ld16(object, 0x188U);
        if (f188 == 0U)
            recovered_state_locomotion_st32(object, 0x1c4U,
                recovered_state_locomotion_cfg_u32(cfg, 0x558U));
        else if (f188 == 1U)
            recovered_state_locomotion_st32(object, 0x1c4U,
                recovered_state_locomotion_cfg_u32(cfg, 0x55cU));
        else
            recovered_state_locomotion_st32(object, 0x1c4U,
                recovered_state_locomotion_cfg_u32(cfg, 0x554U));
        recovered_state_locomotion_st16(object, 0x1b2U, 0U);
        return;
    }
    if (v170 == 5U
            && recovered_state_locomotion_cfg_invoke(
                   object, recovered_state_locomotion_cfg_u32(cfg, 0x3bcU))) {
        f188 = (u32)recovered_state_locomotion_ld16(object, 0x188U);
        if (f188 == 0U)
            recovered_state_locomotion_st32(object, 0x1c4U,
                recovered_state_locomotion_cfg_u32(cfg, 0x564U));
        else if (f188 == 1U)
            recovered_state_locomotion_st32(object, 0x1c4U,
                recovered_state_locomotion_cfg_u32(cfg, 0x568U));
        else
            recovered_state_locomotion_st32(object, 0x1c4U,
                recovered_state_locomotion_cfg_u32(cfg, 0x560U));
        recovered_state_locomotion_st16(object, 0x1b2U, 0U);
        return;
    }

    /* 0x2fc68-0x2fd3c: default clip. */
    {
        volatile unsigned char *record;
        u32 index;
        u32 count;
        u32 f17a;

        f188 = (u32)recovered_state_locomotion_ld16(object, 0x188U);
        index = f188 << 3;
        record = (volatile unsigned char *)(unsigned long)
            recovered_state_locomotion_cfg_u32(cfg, 0xbcU + index);
        recovered_state_locomotion_publish_lo = (u32)(unsigned long)record;
        recovered_state_locomotion_publish_hi =
            recovered_state_locomotion_cfg_u32(cfg, 0xb8U + index);
        count = recovered_state_locomotion_clip_count(record);
        f17a = (u32)recovered_state_locomotion_ld16(object, 0x17aU);

        if (recovered_state_locomotion_sx16(f17a)
                < recovered_state_locomotion_sx16(count)) {
            /* 0x2fce0-0x2fcf8: +0x17a += 1. */
            recovered_state_locomotion_st16(object, 0x17aU, f17a + 1U);
            recovered_state_locomotion_counter_a = (u16)f17a; /* 0x51ab10 */
            recovered_state_locomotion_counter_b = (u16)f17a; /* 0x51ab12 */
        } else {
            /* 0x2fcc8-0x2fcd8: clip end zeroes +0x17a and the counters. */
            recovered_state_locomotion_st16(object, 0x17aU, 0U);
            recovered_state_locomotion_counter_a = 0U;        /* 0x51ab10 */
            recovered_state_locomotion_counter_b = 0U;        /* 0x51ab12 */
        }

        if (f188 == 0U)
            recovered_state_locomotion_st32(object, 0x1c4U,
                recovered_state_locomotion_cfg_u32(cfg, 0x540U));
        else if (f188 == 1U)
            recovered_state_locomotion_st32(object, 0x1c4U,
                recovered_state_locomotion_cfg_u32(cfg, 0x544U));
        else
            recovered_state_locomotion_st32(object, 0x1c4U,
                recovered_state_locomotion_cfg_u32(cfg, 0x53cU));
        recovered_state_locomotion_st16(object, 0x1b2U, 0U);
    }
}

/*
 * State 17 (0x2fd50).  Clip-end reset keyed by +0x188: publish cfg+0xd8/0xdc
 * (+0x188 * 8), advance +0x17a, and on clip end set +0x172 = 0, +0x170 = 1,
 * +0x194 = +0x178 = +0x17a = 0 and +0x1a8 = 2.  +0x1c4 = 0 and +0x1b2 = 0 on
 * both paths.
 */
void recovered_state_locomotion_17_run(volatile unsigned char *object)
{
    volatile unsigned char *cfg = recovered_state_locomotion_config(object);
    u32 f188 = (u32)recovered_state_locomotion_ld16(object, 0x188U);
    u32 index = f188 << 3;
    volatile unsigned char *record = (volatile unsigned char *)(unsigned long)
        recovered_state_locomotion_cfg_u32(cfg, 0xdcU + index);
    u32 count = recovered_state_locomotion_clip_count(record);
    u32 f17a = (u32)recovered_state_locomotion_ld16(object, 0x17aU);

    recovered_state_locomotion_publish_lo = (u32)(unsigned long)record;
                                                             /* 0x51ab08 */
    recovered_state_locomotion_publish_hi =
        recovered_state_locomotion_cfg_u32(cfg, 0xd8U + index);
                                                             /* 0x51ab0c */

    if (recovered_state_locomotion_sx16(f17a)
            < recovered_state_locomotion_sx16(count) - 1) {
        /* 0x2fe00-0x2fe18: +0x17a += 1. */
        recovered_state_locomotion_st16(object, 0x17aU, f17a + 1U);
        recovered_state_locomotion_counter_a = (u16)f17a;    /* 0x51ab10 */
        recovered_state_locomotion_counter_b = (u16)f17a;    /* 0x51ab12 */
    } else {
        /* 0x2fdc4-0x2fdfc: clip end -> +0x172 = 0, +0x170 = 1, +0x1a8 = 2. */
        recovered_state_locomotion_st16(object, 0x172U, 0U);
        recovered_state_locomotion_st16(object, 0x170U, 1U);
        recovered_state_locomotion_st16(object, 0x194U, 0U);
        recovered_state_locomotion_st16(object, 0x178U, 0U);
        recovered_state_locomotion_st16(object, 0x17aU, 0U);
        recovered_state_locomotion_counter_a = (u16)(count - 1U);
        recovered_state_locomotion_counter_b = (u16)(count - 1U);
        recovered_state_locomotion_st8(object, 0x1a8U, 2U);
    }

    /* 0x2fe1c/0x2fe20. */
    recovered_state_locomotion_st32(object, 0x1c4U, 0U);
    recovered_state_locomotion_st16(object, 0x1b2U, 0U);
}

/*
 * State 32 (0x30c20).  Locomotion clip -> idle keyed by +0x176: publish
 * cfg+0x108/0x10c (+0x176 * 32), advance +0x17a (+0x1af = 4 on the advance
 * path), and on clip end set +0x172 = 0, +0x170 = 1, +0x194 = +0x178 =
 * +0x17a = 0 and +0x1a8 = 2.  +0x1c4 is cfg+0x570/0x574/0x56c by +0x176.
 */
void recovered_state_locomotion_32_run(volatile unsigned char *object)
{
    volatile unsigned char *cfg = recovered_state_locomotion_config(object);
    u32 f176 = (u32)recovered_state_locomotion_ld16(object, 0x176U);
    u32 index = f176 << 5;
    volatile unsigned char *record = (volatile unsigned char *)(unsigned long)
        recovered_state_locomotion_cfg_u32(cfg, 0x10cU + index);
    u32 count = recovered_state_locomotion_clip_count(record);
    u32 f17a = (u32)recovered_state_locomotion_ld16(object, 0x17aU);

    recovered_state_locomotion_publish_hi =
        recovered_state_locomotion_cfg_u32(cfg, 0x108U + index);
                                                             /* 0x51ab0c */
    recovered_state_locomotion_publish_lo = (u32)(unsigned long)record;
                                                             /* 0x51ab08 */

    if (recovered_state_locomotion_sx16(f17a)
            < recovered_state_locomotion_sx16(count) - 1) {
        /* 0x30cd4-0x30cf4: +0x1af = 4 and +0x17a += 1. */
        recovered_state_locomotion_st8(object, 0x1afU, 4U);
        recovered_state_locomotion_st16(object, 0x17aU, f17a + 1U);
        recovered_state_locomotion_counter_a = (u16)f17a;    /* 0x51ab10 */
        recovered_state_locomotion_counter_b = (u16)f17a;    /* 0x51ab12 */
    } else {
        /* 0x30c94-0x30cd0: clip end -> +0x172 = 0, +0x170 = 1, +0x1a8 = 2. */
        recovered_state_locomotion_st16(object, 0x172U, 0U);
        recovered_state_locomotion_st16(object, 0x170U, 1U);
        recovered_state_locomotion_st16(object, 0x194U, 0U);
        recovered_state_locomotion_st16(object, 0x178U, 0U);
        recovered_state_locomotion_st16(object, 0x17aU, 0U);
        recovered_state_locomotion_st32(object, 0x1c4U, 0U);
        recovered_state_locomotion_counter_a = (u16)(count - 1U);
        recovered_state_locomotion_counter_b = (u16)(count - 1U);
        recovered_state_locomotion_st8(object, 0x1a8U, 2U);
    }

    /* 0x30cf8-0x30d34: +0x1c4 by +0x176. */
    if (f176 == 0U)
        recovered_state_locomotion_st32(object, 0x1c4U,
            recovered_state_locomotion_cfg_u32(cfg, 0x570U));
    else if (f176 == 1U)
        recovered_state_locomotion_st32(object, 0x1c4U,
            recovered_state_locomotion_cfg_u32(cfg, 0x574U));
    else
        recovered_state_locomotion_st32(object, 0x1c4U,
            recovered_state_locomotion_cfg_u32(cfg, 0x56cU));
    /* State 32 writes no +0x1b2. */
}

/*
 * State 36 (0x31210).  Sibling of state 34: +0x170 = 0, the weapon sentinel
 * gate sets +0x174, publish cfg+0x368/0x36c (+0x176 * 8 + +0x17e * 32),
 * +0x1c4 = cfg+0x570/0x574/0x56c by +0x176, then the clip scan.  Clip end
 * commits +0x172 = 31, +0x170 = 0, +0x17a = 0, +0x17e = 1, +0x1a0 = 0,
 * +0x1a8 = +0x1a9 = 1 and +0x4e += cfg+0x658 while it stays below cfg+0x660.
 * State 36 writes no +0x1b2.
 */
void recovered_state_locomotion_36_run(volatile unsigned char *object)
{
    volatile unsigned char *cfg = recovered_state_locomotion_config(object);
    u32 f176 = (u32)recovered_state_locomotion_ld16(object, 0x176U);
    u32 f17e = (u32)recovered_state_locomotion_ld16(object, 0x17eU);
    u32 index = (f176 << 3) + (f17e << 5);
    volatile unsigned char *record = (volatile unsigned char *)(unsigned long)
        recovered_state_locomotion_cfg_u32(cfg, 0x36cU + index);
    u32 count = recovered_state_locomotion_clip_count(record);
    u32 f17a = (u32)recovered_state_locomotion_ld16(object, 0x17aU);
    u32 selector;

    /* 0x31220: +0x170 = 0. */
    recovered_state_locomotion_st16(object, 0x170U, 0U);

    recovered_state_locomotion_publish_hi =
        recovered_state_locomotion_cfg_u32(cfg, 0x368U + index);
                                                             /* 0x51ab0c */
    recovered_state_locomotion_publish_lo = (u32)(unsigned long)record;
                                                             /* 0x51ab08 */

    /* 0x3128c-0x312ac: +0x1c4 by +0x176. */
    if (f176 == 0U)
        recovered_state_locomotion_st32(object, 0x1c4U,
            recovered_state_locomotion_cfg_u32(cfg, 0x570U));
    else if (f176 == 1U)
        recovered_state_locomotion_st32(object, 0x1c4U,
            recovered_state_locomotion_cfg_u32(cfg, 0x574U));
    else
        recovered_state_locomotion_st32(object, 0x1c4U,
            recovered_state_locomotion_cfg_u32(cfg, 0x56cU));

    /* 0x312b0-0x31314: weapon sentinels set +0x174. */
    if (recovered_state_locomotion_weapon_gate(object, &selector))
        recovered_state_locomotion_st16(object, 0x174U, selector);

    if (recovered_state_locomotion_sx16(f17a)
            < recovered_state_locomotion_sx16(count) - 1) {
        /* 0x313b4-0x313cc: +0x17a += 1. */
        recovered_state_locomotion_st16(object, 0x17aU, f17a + 1U);
        recovered_state_locomotion_counter_a = (u16)f17a;    /* 0x51ab10 */
        recovered_state_locomotion_counter_b = (u16)f17a;    /* 0x51ab12 */
        return;
    }

    /* 0x31340-0x31378: clip end -> state 31. */
    recovered_state_locomotion_st16(object, 0x172U, 31U);
    recovered_state_locomotion_st16(object, 0x170U, 0U);
    recovered_state_locomotion_st16(object, 0x17aU, 0U);
    recovered_state_locomotion_st16(object, 0x17eU, 1U);
    recovered_state_locomotion_st16(object, 0x1a0U, 0U);
    recovered_state_locomotion_counter_a = (u16)(count - 1U);
    recovered_state_locomotion_counter_b = (u16)(count - 1U);
    recovered_state_locomotion_st8(object, 0x1a8U, 1U);
    recovered_state_locomotion_st8(object, 0x1a9U, 1U);

    /* 0x3137c-0x313b0: +0x4e += cfg+0x658 while below cfg+0x660. */
    {
        s32 g4 = recovered_state_locomotion_sx16(
            (u32)recovered_state_locomotion_ld16(object, 0x4eU))
                + (s32)recovered_state_locomotion_cfg_u32(cfg, 0x658U);

        if (g4 < (s32)recovered_state_locomotion_cfg_u32(cfg, 0x660U)) {
            u32 sum = recovered_state_locomotion_cfg_u32(cfg, 0x658U)
                    + (u32)recovered_state_locomotion_ld16(object, 0x4eU);

            recovered_state_locomotion_st16(object, 0x4eU, sum);
        }
    }
}
