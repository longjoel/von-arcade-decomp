/* Bounded freestanding recovery of the i960 0x37130 frame-step state table
 * arms.  The 0x37130 table is the input-facing locomotion dispatcher used by
 * the 0x371e0 per-object frame step (state 0 -> 0x36460, recovered separately
 * in recovered_action_31.c).  Each arm consumes the latched command
 * object+0x137 and routes the object into a locomotion state.
 *
 * Table mapping (0x37130 + state*4):
 *   15 0x36690  16 0x367f0  17 0x36980  19 0x36c40  23 0x36af0
 *   24 0x36bb0  26 0x36cc0  28 0x36d50  29 0x36de0  31 0x36e70
 *   33 0x36ef0  35 0x36f90  37 0x37060
 *
 * Arms 15/16 share the "addo 31,3" route to state 34 and the +0x102-keyed
 * +0x188 classifier:
 *   15 0x36690-0x367ec  state 34, +0x186 = 0
 *   16 0x367f0-0x36970  state 34, +0x186 = 0x18370[action] >> 1; on 0xff it
 *                       routes to state 17 (mode 2/3) or state 0
 * Arm 17 (0x36980-0x36ae4) shares the state-0 route (state 31 +
 * 0x18350/0x18360, +0x186 = 0) plus the object+0x4e accumulator; on 0xff it
 * classifies +0x102 and lands in state 16.
 *
 * The 0x18350/0x18360/0x18370 tables live above the generated span and are
 * read verbatim by the _run wrappers; the pure cores take them as pointers.
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed short s16;
typedef signed int s32;

#define RECOVERED_FRAMESTATE_TABLE_18350 0x00018350UL
#define RECOVERED_FRAMESTATE_TABLE_18360 0x00018360UL
#define RECOVERED_FRAMESTATE_TABLE_18370 0x00018370UL
#define RECOVERED_FRAMESTATE_CONFIG_OFFSET 0x6cU

struct recovered_framestate_context {
    const volatile u16 *table_18350;
    const volatile u16 *table_18360;
    const volatile u16 *table_18370;
};

static u16 recovered_framestate_ld16(const volatile unsigned char *object,
                                     u32 offset)
{
    return *(const volatile u16 *)(object + offset);
}

static u8 recovered_framestate_ld8(const volatile unsigned char *object,
                                   u32 offset)
{
    return *(const volatile u8 *)(object + offset);
}

static void recovered_framestate_st16(volatile unsigned char *object,
                                      u32 offset, u32 value)
{
    *(volatile u16 *)(object + offset) = (u16)value;
}

static void recovered_framestate_st8(volatile unsigned char *object,
                                     u32 offset, u32 value)
{
    *(volatile u8 *)(object + offset) = (u8)value;
}

static u32 recovered_framestate_action(const volatile unsigned char *object)
{
    return (u32)recovered_framestate_ld8(object, 0x137U) & 0xffU;
}

/* 0x367d8-0x367e8 / 0x3695c-0x3696c / 0x36ad0-0x36ae0: +0x1a8 0 -> 2. */
static void recovered_framestate_tail_sentinel(volatile unsigned char *object)
{
    if (recovered_framestate_ld8(object, 0x1a8U) != 0U)
        recovered_framestate_st8(object, 0x1a8U, 2U);
}

/* 0x36744-0x367d4 / 0x368d0-0x36958 / 0x36a44-0x36ab8: the +0x102-keyed
 * +0x188 classifier.  Returns 0..3. */
static u32 recovered_framestate_classify(u32 v102)
{
    u32 t = (v102 + 0xefffU) & 0xffffU;

    if (!(0xfffU < t))
        return 2U;
    t = (v102 + 0xdfffU) & 0xffffU;
    if (!(t > 0x3ffeU))
        return 1U;
    t = (v102 + 0xa000U) & 0xffffU;
    if (0xfffU < t)
        return 0U;
    return 3U;
}

/* 0x366b4-0x3671c / 0x36814-0x36894: action != 0xff -> target state with the
 * direction tables.  g186_from_18370 selects the +0x186 source. */
static void recovered_framestate_route(
    volatile unsigned char *object,
    const struct recovered_framestate_context *ctx,
    u32 target, u32 g186_from_18370)
{
    u32 action = recovered_framestate_action(object);
    u32 word;

    recovered_framestate_st16(object, 0x172U, target);
    recovered_framestate_st16(object, 0x170U, 0U);

    word = (u32)ctx->table_18350[action];
    recovered_framestate_st16(object, 0x176U, word);
    recovered_framestate_st16(object, 0x188U, word);

    recovered_framestate_st16(object, 0x3cU,
        (u32)(s32)(s16)(u16)recovered_framestate_ld16(object, 0x184U)
            + (u32)(s32)(s16)(u16)ctx->table_18360[action]);

    if (g186_from_18370)
        recovered_framestate_st16(object, 0x186U,
            ((u32)(u16)ctx->table_18370[action]) >> 1);
    else
        recovered_framestate_st16(object, 0x186U, 0U);

    recovered_framestate_st16(object, 0x174U, 0U);
    recovered_framestate_st16(object, 0x17eU, 0U);
    recovered_framestate_st16(object, 0x17aU, 0U);
    recovered_framestate_st16(object, 0x1a0U, 0U);
    recovered_framestate_st8(object, 0x1a8U, 1U);
    recovered_framestate_st8(object, 0x1a9U, 1U);
}

/* 0x36a0c-0x36a40: advance object+0x4e by cfg+0x658 up to cfg+0x660. */
static void recovered_framestate_accumulate(volatile unsigned char *object)
{
    volatile unsigned char *cfg = (volatile unsigned char *)(unsigned long)
        *(volatile u32 *)(object + RECOVERED_FRAMESTATE_CONFIG_OFFSET);
    u32 current = (u32)(s32)(s16)(u16)recovered_framestate_ld16(object, 0x4eU);
    u32 step = *(const volatile u32 *)(cfg + 0x658U);
    u32 limit = *(const volatile u32 *)(cfg + 0x660U);

    if (!((step + current) >= limit)) {
        recovered_framestate_st16(object, 0x4eU,
            *(const volatile u32 *)(cfg + 0x658U)
                + recovered_framestate_ld16(object, 0x4eU));
    }
}

/* Returns 1 when the arm routed to state 34 (state 15). */
u32 recovered_framestate_state_15(
    volatile unsigned char *object,
    const struct recovered_framestate_context *ctx)
{
    if (recovered_framestate_action(object) != 0xffU) {
        recovered_framestate_route(object, ctx, 34U, 0U);
        return 1U;
    }

    if ((recovered_framestate_ld16(object, 0x102U) & 0x8000U) != 0U) {
        recovered_framestate_st16(object, 0x172U, 0U);
        recovered_framestate_st16(object, 0x170U, 1U);
        recovered_framestate_st16(object, 0x194U, 0U);
        recovered_framestate_st16(object, 0x178U, 0U);
        recovered_framestate_st16(object, 0x17aU, 0U);
        return 0U;
    }

    if ((recovered_framestate_ld16(object, 0x186U) & 0x8000U) == 0U) {
        u32 v186 = (u32)(s32)(s16)(u16)
            recovered_framestate_ld16(object, 0x186U);
        u32 v102 = (u32)(s32)(s16)(u16)
            recovered_framestate_ld16(object, 0x102U);

        if (v186 != v102) {
            recovered_framestate_st16(object, 0x186U,
                recovered_framestate_ld16(object, 0x102U));
            recovered_framestate_st16(object, 0x188U,
                recovered_framestate_classify(v102));
        }
    }
    recovered_framestate_tail_sentinel(object);
    return 0U;
}

/* Returns 1 when the arm routed to state 34 (state 16). */
u32 recovered_framestate_state_16(
    volatile unsigned char *object,
    const struct recovered_framestate_context *ctx)
{
    if (recovered_framestate_action(object) != 0xffU) {
        recovered_framestate_route(object, ctx, 34U, 1U);
        recovered_framestate_tail_sentinel(object);
        return 1U;
    }

    if ((recovered_framestate_ld16(object, 0x102U) & 0x8000U) != 0U) {
        u32 mode = recovered_framestate_ld16(object, 0x170U);

        if (mode == 2U || mode == 3U) {
            recovered_framestate_st16(object, 0x172U, 17U);
            recovered_framestate_st16(object, 0x17aU, 0U);
        } else {
            recovered_framestate_st16(object, 0x172U, 0U);
            recovered_framestate_st16(object, 0x17aU, 0U);
            recovered_framestate_st16(object, 0x194U, 0U);
        }
        recovered_framestate_tail_sentinel(object);
        return 0U;
    }

    if ((recovered_framestate_ld16(object, 0x186U) & 0x8000U) == 0U) {
        u32 v186 = (u32)(s32)(s16)(u16)
            recovered_framestate_ld16(object, 0x186U);
        u32 v102 = (u32)(s32)(s16)(u16)
            recovered_framestate_ld16(object, 0x102U);

        if (v186 != v102) {
            recovered_framestate_st16(object, 0x186U,
                recovered_framestate_ld16(object, 0x102U));
            recovered_framestate_st16(object, 0x188U,
                recovered_framestate_classify(v102));
        }
    }
    recovered_framestate_tail_sentinel(object);
    return 0U;
}

/* Returns 1 when the arm routed to state 31 (state 17). */
u32 recovered_framestate_state_17(
    volatile unsigned char *object,
    const struct recovered_framestate_context *ctx)
{
    if (recovered_framestate_action(object) != 0xffU) {
        recovered_framestate_route(object, ctx, 31U, 0U);
        recovered_framestate_accumulate(object);
        return 1U;
    }

    if ((recovered_framestate_ld16(object, 0x102U) & 0x8000U) != 0U) {
        recovered_framestate_st16(object, 0x186U, 0U);
        recovered_framestate_tail_sentinel(object);
        return 0U;
    }

    {
        u32 v102 = (u32)(s32)(s16)(u16)
            recovered_framestate_ld16(object, 0x102U);

        recovered_framestate_st16(object, 0x186U,
            recovered_framestate_ld16(object, 0x102U));
        recovered_framestate_st16(object, 0x188U,
            recovered_framestate_classify(v102));
        recovered_framestate_st16(object, 0x172U, 16U);
        recovered_framestate_st16(object, 0x17aU, 0U);
    }
    recovered_framestate_tail_sentinel(object);
    return 0U;
}

/* 0x18438: opposite-direction test (0<->1, 2<->3). */
static u32 recovered_framestate_opposite(u32 a, u32 b)
{
    return ((a == 0U && b == 1U) || (a == 1U && b == 0U)
            || (a == 2U && b == 3U) || (a == 3U && b == 2U)) ? 1U : 0U;
}

/* Returns 1 when the arm routed to state 32 (state 31, 0x36e70). */
u32 recovered_framestate_state_31(
    volatile unsigned char *object,
    const struct recovered_framestate_context *ctx)
{
    u32 action;

    if (!((u32)(s32)(s16)(u16)recovered_framestate_ld16(object, 0x17eU) > 0U))
        return 0U;
    if (recovered_framestate_ld16(object, 0x174U) != 0U)
        return 0U;

    action = recovered_framestate_action(object);
    if (action == 0xffU)
        return 0U;

    if (!recovered_framestate_opposite(
            (u32)(s32)(s16)(u16)recovered_framestate_ld16(object, 0x176U),
            (u32)(s32)(s16)(u16)ctx->table_18350[action]))
        return 0U;

    recovered_framestate_st16(object, 0x172U, 32U);
    if (recovered_framestate_ld16(object, 0x1b2U) == 9U)
        recovered_framestate_st16(object, 0x1b2U, 10U);
    recovered_framestate_st16(object, 0x17aU, 0U);
    return 1U;
}

/* State 33, 0x36ef0-0x36f80: +0x174 != 0 -> state 16 with the +0x102 turn. */
u32 recovered_framestate_state_33(
    volatile unsigned char *object,
    const struct recovered_framestate_context *ctx)
{
    u32 v102;
    u32 t;
    u32 v34;

    (void)ctx;
    if (recovered_framestate_ld16(object, 0x174U) == 0U)
        return 0U;

    recovered_framestate_st16(object, 0x188U,
        recovered_framestate_ld16(object, 0x176U));
    recovered_framestate_st16(object, 0x172U, 16U);

    v102 = recovered_framestate_ld16(object, 0x102U);
    t = (v102 + 0xdfffU) & 0xffffU;
    recovered_framestate_st16(object, 0x186U, v102);

    if (0x3ffeU < t)
        v34 = (v102 & 0xffffU) << 1;
    else
        v34 = (0x8000U + (v102 & 0xffffU) * 2U) & 0xffffU;

    recovered_framestate_st16(object, 0x34U, v34);
    recovered_framestate_st16(object, 0x2eU,
        recovered_framestate_ld16(object, 0x34U)
            + recovered_framestate_ld16(object, 0x184U));
    recovered_framestate_st16(object, 0x178U, 0U);
    recovered_framestate_st16(object, 0x17aU, 0U);
    return 1U;
}

/* States 35 (0x36f90-0x37050) and 37 (0x37060-0x37120): the identical air /
 * landing arms.  Gravity comes from cfg+0x62c; the vertical velocity is the
 * float at object+0x150. */
u32 recovered_framestate_air(
    volatile unsigned char *object, const struct recovered_framestate_context *ctx)
{
    volatile unsigned char *cfg = (volatile unsigned char *)(unsigned long)
        *(volatile u32 *)(object + RECOVERED_FRAMESTATE_CONFIG_OFFSET);

    (void)ctx;
    if (!((u32)(s32)(s16)(u16)recovered_framestate_ld16(object, 0x17aU) > 0U))
        return 0U;

    {
        u32 vy = *(volatile u32 *)(object + 0x150U);
        int negative = (vy & 0x80000000U) != 0U && (vy & 0x7fffffffU) != 0U;

        if (!negative) {
            /* 0x37004 / 0x370d4: rising or level. */
            if (recovered_framestate_ld16(object, 0x180U) == 15U) {
                recovered_framestate_st16(object, 0x172U, 27U);
                recovered_framestate_st16(object, 0x178U, 0U);
                recovered_framestate_st16(object, 0x17aU, 0U);
                recovered_framestate_st16(object, 0x17eU, 0U);
                recovered_framestate_st16(object, 0x1b2U, 0U);
                return 1U;
            }
            recovered_framestate_st16(object, 0x172U, 24U);
            recovered_framestate_st16(object, 0x17aU, 0U);
            if (recovered_framestate_ld16(object, 0x170U) == 2U)
                recovered_framestate_st16(object, 0x17cU, 1U);
            recovered_framestate_st16(object, 0x178U, 0U);
            recovered_framestate_st16(object, 0x1b2U, 0U);
            return 1U;
        }
    }

    /* 0x36fb8-0x37000: falling. */
    if (recovered_framestate_ld8(object, 0x138U) == 0xffU
            && recovered_framestate_ld16(object, 0x170U) != 2U) {
        recovered_framestate_st16(object, 0x170U, 2U);
        recovered_framestate_st16(object, 0x178U, 0U);
        recovered_framestate_st16(object, 0x17cU, 0U);
        recovered_framestate_st16(object, 0x174U, 0U);
    }
    {
        volatile float *vy = (volatile float *)(object + 0x150U);
        volatile float *gravity = (volatile float *)(cfg + 0x62cU);
        *vy = *vy - *gravity;
    }
    recovered_framestate_st16(object, 0x1b2U, 7U);
    return 1U;
}

/* Absolute-global entries. */
static void recovered_framestate_context_init(
    struct recovered_framestate_context *ctx)
{
    ctx->table_18350 = (const volatile u16 *)(unsigned long)
        RECOVERED_FRAMESTATE_TABLE_18350;
    ctx->table_18360 = (const volatile u16 *)(unsigned long)
        RECOVERED_FRAMESTATE_TABLE_18360;
    ctx->table_18370 = (const volatile u16 *)(unsigned long)
        RECOVERED_FRAMESTATE_TABLE_18370;
}

u32 recovered_framestate_state_15_run(volatile unsigned char *object)
{
    struct recovered_framestate_context ctx;

    recovered_framestate_context_init(&ctx);
    return recovered_framestate_state_15(object, &ctx);
}

u32 recovered_framestate_state_16_run(volatile unsigned char *object)
{
    struct recovered_framestate_context ctx;

    recovered_framestate_context_init(&ctx);
    return recovered_framestate_state_16(object, &ctx);
}

u32 recovered_framestate_state_17_run(volatile unsigned char *object)
{
    struct recovered_framestate_context ctx;

    recovered_framestate_context_init(&ctx);
    return recovered_framestate_state_17(object, &ctx);
}

u32 recovered_framestate_state_31_run(volatile unsigned char *object)
{
    struct recovered_framestate_context ctx;

    recovered_framestate_context_init(&ctx);
    return recovered_framestate_state_31(object, &ctx);
}

u32 recovered_framestate_state_33_run(volatile unsigned char *object)
{
    struct recovered_framestate_context ctx;

    recovered_framestate_context_init(&ctx);
    return recovered_framestate_state_33(object, &ctx);
}

u32 recovered_framestate_air_35_run(volatile unsigned char *object)
{
    struct recovered_framestate_context ctx;

    recovered_framestate_context_init(&ctx);
    return recovered_framestate_air(object, &ctx);
}

u32 recovered_framestate_air_37_run(volatile unsigned char *object)
{
    struct recovered_framestate_context ctx;

    recovered_framestate_context_init(&ctx);
    return recovered_framestate_air(object, &ctx);
}
