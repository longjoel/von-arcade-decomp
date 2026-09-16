/* Bounded freestanding runnable recovery of the i960 per-object dash / boost
 * state handler at 0x31d20-0x32114 (state 20 of the 0x32560 state table).
 *
 * Provenance
 * ----------
 * State 20 is the only handler that reads the latched action selector
 * object+0x136 (0x31fb4/0x31ff4/0x3200c), so it is the committed-input ->
 * state-machine bridge.  It is reached from the dash/boost family and hands off
 * to the attack/air states 36-40 (0x31e84, 0x31ee8, 0x31f2c, 0x31f70, 0x31fc4)
 * or back to the idle/turn states 11/21 (0x320b8, 0x320dc).  Every exit path
 * clears the cruise speed object+0x1c4.
 *
 * Listing map (base register g0 = object, cfg = [object+0x6c]):
 *
 *   0x31d30  stos g14,0x170(g0)        +0x170 = 0
 *   0x31d34  ldos 0x174(g0)            +0x174 selects the cfg table pair
 *   0x31d3c  cfg+0x290/0x294 indexed by (+0x176 & 3) * 32 -> g4 / g6
 *   0x31d70  cfg+0x288/0x28c (same index) when +0x174 == 0
 *   0x31da0  st g6,0x51ab08 / st g4,0x51ab0c   shadow publication
 *   0x31db8  ldos 0x4(g6)              clip count from the published record
 *   0x31dc0  +0x17a++ ; +0x106 vs +0x108 mismatch advances +0x17a again
 *   0x31dd8  0x51ab10 / 0x51ab12 = clip - 1
 *   0x31e08  +0x1b2 = 5 ; +0x644>>1 timer gates +0x180 ; +0x190 = 2
 *   0x31e4c  +0x17a < cfg+0x644 ends the frame (speed 0)
 *   0x31e50  +0x1b2 = 7 ; +0x180 sub-mode 9/10/11/12 select states 37-40
 *   0x31f98  the object+0x143 / object+0x142 / object+0x136 action bridge
 *   0x32094  the idle fall-through (state 11 or 21)
 *   0x3210c  st g14,0x1c4(g0)          +0x1c4 = 0
 *
 * The 0x18380 / 0x18350 / 0x18360 tables live above the reconstructed image
 * (the generated span ends at 0xf9b0) and are read verbatim by the _run
 * wrapper; the pure core takes them as base pointers so the host build never
 * dereferences a target address.  The 0x51ab08/0x51ab0c/0x51ab10/0x51ab12
 * absolute scratch cells are file-static stand-ins re-homed by _run.
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed short s16;
typedef signed int s32;

#define RECOVERED_STATE_DASH_CONFIG_OFFSET 0x6cU

#define RECOVERED_STATE_DASH_TABLE_18380 0x00018380UL
#define RECOVERED_STATE_DASH_TABLE_18350 0x00018350UL
#define RECOVERED_STATE_DASH_TABLE_18360 0x00018360UL

#define RECOVERED_STATE_DASH_SHADOW_LO 0x0051ab08UL
#define RECOVERED_STATE_DASH_SHADOW_HI 0x0051ab0cUL
#define RECOVERED_STATE_DASH_COUNTER_A 0x0051ab10UL
#define RECOVERED_STATE_DASH_COUNTER_B 0x0051ab12UL

/* 0x18380: address = base + (s16)+0x176 * 2 + (s16)+0x174 * 8. */
static u16 recovered_state_dash_lookup_18380(const volatile u16 *base,
                                             u32 v174, u32 v176)
{
    const volatile u16 *entry = (const volatile u16 *)
        ((const volatile u8 *)base
            + (s32)(s16)(u16)v176 * 2
            + (s32)(s16)(u16)v174 * 8);

    return *entry;
}

/* 0x18350/0x18360: halfword table indexed by the committed action byte. */
static u16 recovered_state_dash_lookup_action(const volatile u16 *base,
                                              u32 action)
{
    return base[action & 0xffU];
}

static volatile unsigned char *recovered_state_dash_config(
    volatile unsigned char *object)
{
    return (volatile unsigned char *)(unsigned long)
        *(volatile u32 *)(object + RECOVERED_STATE_DASH_CONFIG_OFFSET);
}

static u16 recovered_state_dash_ld16(const volatile unsigned char *object,
                                     u32 offset)
{
    return *(const volatile u16 *)(object + offset);
}

static u8 recovered_state_dash_ld8(const volatile unsigned char *object,
                                   u32 offset)
{
    return *(const volatile u8 *)(object + offset);
}

static u32 recovered_state_dash_cfg_u32(const volatile unsigned char *cfg,
                                        u32 offset)
{
    return *(const volatile u32 *)(cfg + offset);
}

static void recovered_state_dash_st16(volatile unsigned char *object,
                                      u32 offset, u32 value)
{
    *(volatile u16 *)(object + offset) = (u16)value;
}

static void recovered_state_dash_st8(volatile unsigned char *object,
                                     u32 offset, u32 value)
{
    *(volatile u8 *)(object + offset) = (u8)value;
}

static void recovered_state_dash_st32(volatile unsigned char *object,
                                      u32 offset, u32 value)
{
    *(volatile u32 *)(object + offset) = value;
}

/* shlo 16 / shri 16: sign-extend the low halfword. */
static s32 recovered_state_dash_sx16(u32 value)
{
    return (s32)(s16)(u16)value;
}

struct recovered_state_dash_20_context {
    const volatile u16 *table_18380;
    const volatile u16 *table_18350;
    const volatile u16 *table_18360;
    volatile u32 *shadow_lo;   /* 0x51ab08 */
    volatile u32 *shadow_hi;   /* 0x51ab0c */
    volatile u16 *counter_a;   /* 0x51ab10 */
    volatile u16 *counter_b;   /* 0x51ab12 */
};

/* 0x31e60-0x31e80 / 0x320e0-0x32100: publish the 0x18380 cell into +0x176. */
static void recovered_state_dash_table_into_176(
    volatile unsigned char *object,
    const struct recovered_state_dash_20_context *ctx)
{
    u32 v174 = recovered_state_dash_ld16(object, 0x174U);
    u32 v176 = recovered_state_dash_ld16(object, 0x176U);

    recovered_state_dash_st16(object, 0x176U,
        recovered_state_dash_lookup_18380(ctx->table_18380, v174, v176));
}

/* 0x31f74-0x31f94: shared attack/air hand-off tail (states 38/39/40). */
static void recovered_state_dash_handoff(
    volatile unsigned char *object, u32 state)
{
    volatile unsigned char *cfg = recovered_state_dash_config(object);

    recovered_state_dash_st16(object, 0x172U, state);
    recovered_state_dash_st16(object, 0x170U, 0U);
    recovered_state_dash_st16(object, 0x180U, 0U);
    recovered_state_dash_st16(object, 0x17eU, 0U);
    recovered_state_dash_st16(object, 0x178U, 0U);
    recovered_state_dash_st16(object, 0x17aU, 0U);
    recovered_state_dash_st32(object, 0x190U,
        recovered_state_dash_cfg_u32(cfg, 0x664U));
}

/* 0x32080-0x32090: mode-9 and +0x136 tails publish cfg+0x668. */
static void recovered_state_dash_tail_668(volatile unsigned char *object)
{
    volatile unsigned char *cfg = recovered_state_dash_config(object);

    recovered_state_dash_st32(object, 0x190U,
        recovered_state_dash_cfg_u32(cfg, 0x668U));
}

/* 0x32094-0x3210c: idle fall-through.  object+0x13b and the +0x1dd/0x1de/0x1df
 * air flags select state 11 (clip) or state 21 (turn), then clear +0x1c4. */
static void recovered_state_dash_idle_fallthrough(
    volatile unsigned char *object,
    const struct recovered_state_dash_20_context *ctx)
{
    if (recovered_state_dash_ld8(object, 0x13bU) != 0U
            && ((recovered_state_dash_ld8(object, 0x1deU) & 2U)
                    || (recovered_state_dash_ld8(object, 0x1ddU) & 2U)
                    || (recovered_state_dash_ld8(object, 0x1dfU) & 2U))) {
        recovered_state_dash_st16(object, 0x172U, 11U);
        recovered_state_dash_st16(object, 0x170U, 0U);
        recovered_state_dash_st16(object, 0x176U, 0U);
        recovered_state_dash_st16(object, 0x17eU, 0U);
        recovered_state_dash_st16(object, 0x17aU, 0U);
        recovered_state_dash_st16(object, 0x17cU, 0U);
        recovered_state_dash_st16(object, 0x178U, 0U);
        recovered_state_dash_st16(object, 0x180U, 0U);
    } else {
        recovered_state_dash_st16(object, 0x172U, 21U);
        recovered_state_dash_table_into_176(object, ctx);
        recovered_state_dash_st16(object, 0x17aU, 0U);
        recovered_state_dash_st16(object, 0x180U, 0U);
    }
    recovered_state_dash_st32(object, 0x1c4U, 0U);
}

/* 0x31f98-0x32090: the committed-action bridge. */
static void recovered_state_dash_action_bridge(
    volatile unsigned char *object,
    const struct recovered_state_dash_20_context *ctx)
{
    volatile unsigned char *cfg;
    u32 action;

    /* 0x31f98-0x31fb0: object+0x143 != 0, or object+0x142 != 0, reaches the
     * action test; otherwise the idle fall-through at 0x32094 runs. */
    if (recovered_state_dash_ld8(object, 0x143U) == 0U
            && (u32)recovered_state_dash_ld8(object, 0x142U) == 0U) {
        recovered_state_dash_idle_fallthrough(object, ctx);
        return;
    }

    action = (u32)recovered_state_dash_ld8(object, 0x136U) & 0xffU;
    if (action == 0xffU) {                              /* 0x31fbc */
        recovered_state_dash_idle_fallthrough(object, ctx);
        return;
    }

    /* 0x31fc0-0x3204c: state 36, then the action-keyed 0x18350/0x18360
     * lookups build +0x176/+0x188 and the object+0x3c turn target. */
    recovered_state_dash_st16(object, 0x172U, 36U);
    recovered_state_dash_st16(object, 0x170U, 0U);
    recovered_state_dash_st16(object, 0x180U, 0U);
    recovered_state_dash_table_into_176(object, ctx);
    recovered_state_dash_st16(object, 0x176U,
        recovered_state_dash_lookup_action(ctx->table_18350, action));
    recovered_state_dash_st16(object, 0x188U,
        recovered_state_dash_lookup_action(ctx->table_18350, action));
    recovered_state_dash_st16(object, 0x3cU,
        (u32)(s32)(s16)(u16)recovered_state_dash_ld16(object, 0x184U)
            + (u32)recovered_state_dash_sx16(
                  recovered_state_dash_lookup_action(ctx->table_18360, action)));
    recovered_state_dash_st16(object, 0x186U, 0U);
    recovered_state_dash_st16(object, 0x174U, 0U);
    recovered_state_dash_st16(object, 0x17aU, 0U);
    recovered_state_dash_st16(object, 0x1a0U, 0U);
    recovered_state_dash_st8(object, 0x1a8U, 1U);
    recovered_state_dash_st8(object, 0x1a9U, 1U);

    /* 0x3204c-0x3207c: advance the shared object+0x4e accumulator by
     * cfg+0x658, clamped below cfg+0x660. */
    cfg = recovered_state_dash_config(object);
    {
        u32 current = (u32)recovered_state_dash_sx16(
            recovered_state_dash_ld16(object, 0x4eU));
        u32 step = recovered_state_dash_cfg_u32(cfg, 0x658U);
        u32 limit = recovered_state_dash_cfg_u32(cfg, 0x660U);

        if (!((step + current) >= limit)) {
            recovered_state_dash_st16(object, 0x4eU,
                recovered_state_dash_cfg_u32(cfg, 0x658U)
                    + recovered_state_dash_ld16(object, 0x4eU));
        }
    }

    recovered_state_dash_tail_668(object);
    recovered_state_dash_st32(object, 0x1c4U, 0U);
}

void recovered_state_dash_20_core(
    volatile unsigned char *object,
    const struct recovered_state_dash_20_context *ctx)
{
    volatile unsigned char *cfg;
    u32 v174;
    u32 v176;
    u32 index;
    u32 word_a;
    u32 word_b;
    u32 clip;
    u32 sub;
    u32 timer;

    /* 0x31d30-0x31d9c: publish the cfg table pair for the (+0x176 & 3) lane. */
    recovered_state_dash_st16(object, 0x170U, 0U);

    v174 = recovered_state_dash_ld16(object, 0x174U);
    v176 = recovered_state_dash_ld16(object, 0x176U);
    index = (v176 & 3U) * 32U;
    cfg = recovered_state_dash_config(object);

    if (v174 == 0U) {
        word_b = recovered_state_dash_cfg_u32(cfg, 0x28cU + index);
        word_a = recovered_state_dash_cfg_u32(cfg, 0x288U + index);
    } else {
        word_b = recovered_state_dash_cfg_u32(cfg, 0x294U + index);
        word_a = recovered_state_dash_cfg_u32(cfg, 0x290U + index);
    }

    *ctx->shadow_lo = word_b;
    *ctx->shadow_hi = word_a;

    /* 0x31db0-0x31e04: clip count, +0x17a advance, 0x51ab10/0x51ab12. */
    clip = (u32)recovered_state_dash_ld16(
        (const volatile unsigned char *)(unsigned long)word_b, 0x4U);
    recovered_state_dash_st16(object, 0x17aU,
        recovered_state_dash_ld16(object, 0x17aU) + 1U);
    if ((recovered_state_dash_ld16(object, 0x106U) & 0xffffU)
            != (recovered_state_dash_ld16(object, 0x108U) & 0xffffU)) {
        recovered_state_dash_st16(object, 0x17aU,
            recovered_state_dash_ld16(object, 0x17aU) + 1U);
    }
    *ctx->counter_b = (u16)(clip - 1U);
    *ctx->counter_a = (u16)(clip - 1U);

    /* 0x31e08-0x31e28: +0x1b2 = 5, cfg+0x644>>1 gates the +0x180 sub-phase. */
    recovered_state_dash_st16(object, 0x1b2U, 5U);
    timer = recovered_state_dash_cfg_u32(
        recovered_state_dash_config(object), 0x644U);
    if (!(recovered_state_dash_sx16(recovered_state_dash_ld16(object, 0x17aU))
            >= (s32)(timer >> 1))) {
        recovered_state_dash_st16(object, 0x180U, 0U);
    }

    /* 0x31e30-0x31e4c: +0x190 = 2; below cfg+0x644 the frame ends with no
     * cruise speed. */
    recovered_state_dash_st16(object, 0x190U, 2U);
    if (recovered_state_dash_sx16(recovered_state_dash_ld16(object, 0x17aU))
            < (s32)timer) {
        recovered_state_dash_st32(object, 0x1c4U, 0U);
        return;
    }

    /* 0x31e50-0x31f94: +0x1b2 = 7, then the +0x180 sub-mode dispatch. */
    recovered_state_dash_st16(object, 0x1b2U, 7U);
    sub = recovered_state_dash_ld16(object, 0x180U);

    if (sub == 9U) {                                            /* 0x31e5c */
        recovered_state_dash_table_into_176(object, ctx);
        recovered_state_dash_st16(object, 0x172U, 37U);
        recovered_state_dash_st16(object, 0x170U, 0U);
        recovered_state_dash_st16(object, 0x180U, 0U);
        recovered_state_dash_st16(object, 0x17aU, 0U);
        recovered_state_dash_st16(object, 0x1a0U, 0U);
        recovered_state_dash_st8(object, 0x1a8U, 1U);
        recovered_state_dash_st8(object, 0x1a9U, 0U);
        recovered_state_dash_tail_668(object);
        recovered_state_dash_st32(object, 0x1c4U, 0U);
        return;
    }
    if (sub == 11U) {                                           /* 0x31eb0 */
        if ((recovered_state_dash_ld8(object, 0x1ddU) & 2U) != 0U) {
            recovered_state_dash_table_into_176(object, ctx);
            recovered_state_dash_handoff(object, 38U);
            recovered_state_dash_st32(object, 0x1c4U, 0U);
            return;
        }
    } else if (sub == 10U) {                                    /* 0x31ef4 */
        if ((recovered_state_dash_ld8(object, 0x1deU) & 2U) != 0U) {
            recovered_state_dash_table_into_176(object, ctx);
            recovered_state_dash_handoff(object, 39U);
            recovered_state_dash_st32(object, 0x1c4U, 0U);
            return;
        }
    } else if (sub == 12U) {                                    /* 0x31f38 */
        if ((recovered_state_dash_ld8(object, 0x1dfU) & 2U) != 0U) {
            recovered_state_dash_table_into_176(object, ctx);
            recovered_state_dash_handoff(object, 40U);
            recovered_state_dash_st32(object, 0x1c4U, 0U);
            return;
        }
    }

    /* 0x31f98: the committed-action bridge (also the idle fall-through). */
    recovered_state_dash_action_bridge(object, ctx);
}

/* Absolute-global entry, 0x31d20. */
static volatile u32 recovered_state_dash_shadow_lo;
static volatile u32 recovered_state_dash_shadow_hi;
static volatile u16 recovered_state_dash_counter_a;
static volatile u16 recovered_state_dash_counter_b;

void recovered_state_dash_20_run(volatile unsigned char *object)
{
    struct recovered_state_dash_20_context ctx;

    ctx.table_18380 = (const volatile u16 *)(unsigned long)
        RECOVERED_STATE_DASH_TABLE_18380;
    ctx.table_18350 = (const volatile u16 *)(unsigned long)
        RECOVERED_STATE_DASH_TABLE_18350;
    ctx.table_18360 = (const volatile u16 *)(unsigned long)
        RECOVERED_STATE_DASH_TABLE_18360;
    ctx.shadow_lo = &recovered_state_dash_shadow_lo;
    ctx.shadow_hi = &recovered_state_dash_shadow_hi;
    ctx.counter_a = &recovered_state_dash_counter_a;
    ctx.counter_b = &recovered_state_dash_counter_b;

    recovered_state_dash_20_core(object, &ctx);
}
