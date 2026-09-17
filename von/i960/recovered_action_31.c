/* Bounded freestanding recovery of the i960 committed-action -> locomotion
 * transition at 0x36460-0x3668c (the state-0 entry of the per-kind dispatcher
 * table at 0x37130, also inlined at 0x373ac-0x37464).
 *
 * Provenance
 * ----------
 * The 0x24fc0 input consumer latches the decoded command into object+0x137.
 * This handler is the only consumer of that latch that drives locomotion: when
 * +0x137 != 0xff it forces object+0x172 = 31 (the cruise state), clears the
 * sub-phase, and builds the direction from the committed action through the
 * 0x18350 / 0x18360 / 0x18370 halfword tables.  State 31 then selects its
 * cruise speed from cfg+0x56c/0x570/0x574 by object+0x176, so this is the
 * stick/command -> translation link.
 *
 * Listing map (g0 = object, g2 = return):
 *
 *   0x36470  ldos 0x18e ; != 0 -> +0x18e-- and return (cooldown)
 *   0x36488  ldob 0x137 ; == 0xff -> the reload path at 0x36554
 *   0x3649c  stos 31,0x172 ; stos 0,0x170
 *   0x364a8  0x18350[+0x137] -> +0x176 and +0x188
 *   0x364c0  0x18360[+0x137] (s16) added to +0x184 -> +0x3c
 *   0x364e4  0x18370[+0x137] (s16) >> 1 -> +0x186
 *   0x36500  +0x174/+0x17e/+0x17a/+0x1a0 = 0
 *   0x36510  +0x1a8/+0x1a9 = 1
 *   0x3651c  object+0x4e accumulator advanced by cfg+0x658, clamped by cfg+0x660
 *   0x36554  reload: +0x10e != 0 or +0x102 bit15 -> +0x1a8 sentinel and return
 *   0x36574  +0x170 in {2,3} -> state 16, +0x186 = +0x102, +0x188 class, +0x17a = 0
 *   0x365f4  otherwise -> state 15, +0x178 = 0 and +0x17a = 0
 *   0x365e8  the +0x102-keyed 0/1/2/3 classifier shared by both reload arms
 *
 * The 0x18350/0x18360/0x18370 tables live above the generated span and are
 * read verbatim by the _run wrapper; the pure core takes them as pointers.
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed short s16;
typedef signed int s32;

#define RECOVERED_ACTION_31_CONFIG_OFFSET 0x6cU

#define RECOVERED_ACTION_31_TABLE_18350 0x00018350UL
#define RECOVERED_ACTION_31_TABLE_18360 0x00018360UL
#define RECOVERED_ACTION_31_TABLE_18370 0x00018370UL

static volatile unsigned char *recovered_action_31_config(
    volatile unsigned char *object)
{
    return (volatile unsigned char *)(unsigned long)
        *(volatile u32 *)(object + RECOVERED_ACTION_31_CONFIG_OFFSET);
}

static u16 recovered_action_31_ld16(const volatile unsigned char *object,
                                    u32 offset)
{
    return *(const volatile u16 *)(object + offset);
}

static u8 recovered_action_31_ld8(const volatile unsigned char *object,
                                  u32 offset)
{
    return *(const volatile u8 *)(object + offset);
}

static u32 recovered_action_31_cfg_u32(const volatile unsigned char *cfg,
                                       u32 offset)
{
    return *(const volatile u32 *)(cfg + offset);
}

static void recovered_action_31_st16(volatile unsigned char *object,
                                     u32 offset, u32 value)
{
    *(volatile u16 *)(object + offset) = (u16)value;
}

static void recovered_action_31_st8(volatile unsigned char *object,
                                    u32 offset, u32 value)
{
    *(volatile u8 *)(object + offset) = (u8)value;
}

struct recovered_action_31_context {
    const volatile u16 *table_18350;
    const volatile u16 *table_18360;
    const volatile u16 *table_18370;
};

/* 0x3651c-0x36550: advance the shared object+0x4e accumulator. */
static void recovered_action_31_accumulate(volatile unsigned char *object)
{
    volatile unsigned char *cfg = recovered_action_31_config(object);
    u32 current = (u32)(s32)(s16)(u16)recovered_action_31_ld16(object, 0x4eU);
    u32 step = recovered_action_31_cfg_u32(cfg, 0x658U);
    u32 limit = recovered_action_31_cfg_u32(cfg, 0x660U);

    if (!((step + current) >= limit)) {
        recovered_action_31_st16(object, 0x4eU,
            recovered_action_31_cfg_u32(cfg, 0x658U)
                + recovered_action_31_ld16(object, 0x4eU));
    }
}

/* 0x365e8 / 0x36668: the +0x102-keyed +0x188 classifier shared by both reload
 * arms.  Returns 0..3. */
static u32 recovered_action_31_classify(u32 v102)
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

/* 0x36554-0x3668b: the +0x137 == 0xff reload path.  It selects the locomotion
 * reload state from +0x170 and publishes the +0x102 class, or latches the
 * +0x1a8 sentinel and leaves the object untouched.  Always returns 0: this arm
 * never applies the state-31 transition. */
static u32 recovered_action_31_reload(volatile unsigned char *object)
{
    u32 mode;
    u32 v102;

    if (recovered_action_31_ld16(object, 0x10eU) != 0U ||
        (recovered_action_31_ld16(object, 0x102U) & 0x8000U) != 0U) {
        if (recovered_action_31_ld8(object, 0x1a8U) != 0U)
            recovered_action_31_st8(object, 0x1a8U, 2U);
        return 0U;
    }

    mode = recovered_action_31_ld16(object, 0x170U);
    v102 = (u32)recovered_action_31_ld16(object, 0x102U);

    if (mode == 2U || mode == 3U) {
        /* 0x36574-0x365f0: state 16, no +0x178 clear. */
        recovered_action_31_st16(object, 0x172U, 16U);
    } else {
        /* 0x365f4-0x36674: state 15, +0x178 cleared. */
        recovered_action_31_st16(object, 0x172U, 15U);
        recovered_action_31_st16(object, 0x178U, 0U);
    }
    recovered_action_31_st16(object, 0x186U, v102);
    recovered_action_31_st16(object, 0x188U,
        recovered_action_31_classify(v102));
    recovered_action_31_st16(object, 0x17aU, 0U);
    return 0U;
}

/* Returns 1 when the action->state-31 transition was applied. */
u32 recovered_action_31_core(
    volatile unsigned char *object,
    const struct recovered_action_31_context *ctx)
{
    u32 action;
    u32 word;
    u32 delta;

    /* 0x36470-0x36484: cooldown gate. */
    if (recovered_action_31_ld16(object, 0x18eU) != 0U) {
        recovered_action_31_st16(object, 0x18eU,
            recovered_action_31_ld16(object, 0x18eU) - 1U);
        return 0U;
    }

    /* 0x36488-0x36498: a 0xff latch takes the reload path at 0x36554. */
    action = (u32)recovered_action_31_ld8(object, 0x137U) & 0xffU;
    if (action == 0xffU)
        return recovered_action_31_reload(object);

    /* 0x3649c-0x364fc: force state 31 and build the direction. */
    recovered_action_31_st16(object, 0x172U, 31U);
    recovered_action_31_st16(object, 0x170U, 0U);

    word = (u32)ctx->table_18350[action];
    recovered_action_31_st16(object, 0x176U, word);
    recovered_action_31_st16(object, 0x188U, word);

    delta = (u32)(s32)(s16)(u16)ctx->table_18360[action];
    recovered_action_31_st16(object, 0x3cU,
        (u32)(s32)(s16)(u16)recovered_action_31_ld16(object, 0x184U) + delta);

    /* shlo 16 / shri 17: (u16)table >> 1, zero-extended. */
    recovered_action_31_st16(object, 0x186U,
        ((u32)(u16)ctx->table_18370[action]) >> 1);

    /* 0x36500-0x36518. */
    recovered_action_31_st16(object, 0x174U, 0U);
    recovered_action_31_st16(object, 0x17eU, 0U);
    recovered_action_31_st16(object, 0x17aU, 0U);
    recovered_action_31_st16(object, 0x1a0U, 0U);
    recovered_action_31_st8(object, 0x1a8U, 1U);
    recovered_action_31_st8(object, 0x1a9U, 1U);

    recovered_action_31_accumulate(object);
    return 1U;
}

/* Absolute-global entry, 0x36460. */
u32 recovered_action_31_run(volatile unsigned char *object)
{
    struct recovered_action_31_context ctx;

    ctx.table_18350 = (const volatile u16 *)(unsigned long)
        RECOVERED_ACTION_31_TABLE_18350;
    ctx.table_18360 = (const volatile u16 *)(unsigned long)
        RECOVERED_ACTION_31_TABLE_18360;
    ctx.table_18370 = (const volatile u16 *)(unsigned long)
        RECOVERED_ACTION_31_TABLE_18370;

    return recovered_action_31_core(object, &ctx);
}
