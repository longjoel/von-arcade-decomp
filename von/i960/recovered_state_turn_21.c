/* Bounded freestanding runnable recovery of the i960 per-object turn/return
 * state handler at 0x32120-0x32324 (state 21 of the 0x32560 state table).
 *
 * Provenance
 * ----------
 * State 21 is the locomotion sub-phase selector the dash bridge (state 20)
 * falls back to when no committed action is present.  It publishes the
 * cfg+0x2f8/0x2fc record lanes, advances the object+0x17a clip counter, and
 * then, keyed on the object+0x180 sub-phase, writes the object+0x170 movement
 * mode (1/2/3) and returns to states 0/1 -- which are the mode-gated
 * locomotion handlers.  This resolves the "object+0x170 modes 2..5" puzzle:
 * the modes are literal here (2 at 0x32244, 3 at 0x32280), not config data.
 *
 * Listing map (g0 = object, cfg = [object+0x6c], return g2 = 0x32324):
 *
 *   0x32130  stos g14,0x170(g0)        +0x170 = 0
 *   0x32134  cfg+0x2fc[(+0x176&1)*8] -> g6 (0x51ab08)
 *   0x3214c  cfg+0x2f8[(+0x176&1)*8] -> g7 (0x51ab0c)
 *   0x32168  +0x17a++  0x51ab10/0x51ab12 = old +0x17a
 *   0x32184  chkbit 0(+0x17a): odd frames also advance on a command change
 *   0x321bc  +0x190 = 2 ; record clip count = ldos 0x4(g6)
 *   0x321e4  +0x17a < clip ends the frame (+0x1c4 = 0)
 *   0x321e8  +0x13b and the +0x1dd/0x1de/0x1df air flags -> state 11
 *   0x32240  +0x180 == 10 -> +0x170 = 2, state 0
 *   0x3227c  +0x180 == 11 -> +0x170 = 3, state 0
 *   0x322b8  +0x180 == 12 -> state 1
 *   0x322f0  else          -> +0x170 = 1, state 0
 *   0x32314  +0x190 = cfg+0x664 (sub-modes) or cfg+0x668 (else)
 *   0x3231c  st g14,0x1c4(g0)          +0x1c4 = 0
 *
 * The 0x51ab08/0x51ab0c/0x51ab10/0x51ab12 cells are file-static stand-ins; the
 * pure core takes them and the cfg lanes as context so the host build never
 * dereferences a target address.
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed short s16;
typedef signed int s32;

#define RECOVERED_STATE_21_CONFIG_OFFSET 0x6cU

#define RECOVERED_STATE_21_SHADOW_LO 0x0051ab08UL
#define RECOVERED_STATE_21_SHADOW_HI 0x0051ab0cUL
#define RECOVERED_STATE_21_COUNTER_A 0x0051ab10UL
#define RECOVERED_STATE_21_COUNTER_B 0x0051ab12UL

static volatile unsigned char *recovered_state_21_config(
    volatile unsigned char *object)
{
    return (volatile unsigned char *)(unsigned long)
        *(volatile u32 *)(object + RECOVERED_STATE_21_CONFIG_OFFSET);
}

static u16 recovered_state_21_ld16(const volatile unsigned char *object,
                                   u32 offset)
{
    return *(const volatile u16 *)(object + offset);
}

static u8 recovered_state_21_ld8(const volatile unsigned char *object,
                                 u32 offset)
{
    return *(const volatile u8 *)(object + offset);
}

static u32 recovered_state_21_cfg_u32(const volatile unsigned char *cfg,
                                      u32 offset)
{
    return *(const volatile u32 *)(cfg + offset);
}

static void recovered_state_21_st16(volatile unsigned char *object,
                                    u32 offset, u32 value)
{
    *(volatile u16 *)(object + offset) = (u16)value;
}

static void recovered_state_21_st32(volatile unsigned char *object,
                                    u32 offset, u32 value)
{
    *(volatile u32 *)(object + offset) = value;
}

static s32 recovered_state_21_sx16(u32 value)
{
    return (s32)(s16)(u16)value;
}

struct recovered_state_21_context {
    volatile u32 *shadow_lo;   /* 0x51ab08 */
    volatile u32 *shadow_hi;   /* 0x51ab0c */
    volatile u16 *counter_a;   /* 0x51ab10 */
    volatile u16 *counter_b;   /* 0x51ab12 */
};

/* 0x321e8-0x32238: the +0x13b and air-flag branch to state 11. */
static int recovered_state_21_air_gate(const volatile unsigned char *object)
{
    if (recovered_state_21_ld8(object, 0x13bU) == 0U)
        return 0;
    return (recovered_state_21_ld8(object, 0x1deU) & 2U) != 0U
        || (recovered_state_21_ld8(object, 0x1ddU) & 2U) != 0U
        || (recovered_state_21_ld8(object, 0x1dfU) & 2U) != 0U;
}

void recovered_state_21_core(
    volatile unsigned char *object,
    const struct recovered_state_21_context *ctx)
{
    volatile unsigned char *cfg;
    u32 lane;
    u32 word_a;
    u32 word_b;
    u32 old17a;
    u32 new17a;
    u32 clip;
    u32 sub;

    /* 0x32130-0x32188: publish the cfg+0x2f8/0x2fc record lane. */
    recovered_state_21_st16(object, 0x170U, 0U);
    cfg = recovered_state_21_config(object);
    lane = (recovered_state_21_ld16(object, 0x176U) & 1U) * 8U;
    word_b = recovered_state_21_cfg_u32(cfg, 0x2fcU + lane);   /* g6 */
    word_a = recovered_state_21_cfg_u32(cfg, 0x2f8U + lane);   /* g7 */

    old17a = recovered_state_21_ld16(object, 0x17aU);
    *ctx->shadow_lo = word_b;
    *ctx->shadow_hi = word_a;
    *ctx->counter_b = (u16)old17a;
    *ctx->counter_a = (u16)old17a;
    new17a = (old17a + 1U) & 0xffffU;
    recovered_state_21_st16(object, 0x17aU, new17a);

    /* 0x32184-0x321b8: odd +0x17a frames advance again on a command change. */
    if ((new17a & 1U) != 0U
            && (recovered_state_21_ld16(object, 0x106U) & 0xffffU)
                != (recovered_state_21_ld16(object, 0x108U) & 0xffffU)) {
        recovered_state_21_st16(object, 0x17aU,
            recovered_state_21_ld16(object, 0x17aU) + 1U);
    }

    /* 0x321bc-0x321e4: +0x190 = 2; below the record clip count the frame ends
     * with no cruise speed. */
    recovered_state_21_st16(object, 0x190U, 2U);
    clip = (u32)recovered_state_21_ld16(
        (const volatile unsigned char *)(unsigned long)word_b, 0x4U);
    if (recovered_state_21_sx16(recovered_state_21_ld16(object, 0x17aU))
            < (s32)(s16)(u16)clip) {
        recovered_state_21_st32(object, 0x1c4U, 0U);
        return;
    }

    /* 0x321e8-0x32238: state 11 clip hand-off. */
    if (recovered_state_21_air_gate(object)) {
        recovered_state_21_st16(object, 0x172U, 11U);
        recovered_state_21_st16(object, 0x170U, 0U);
        recovered_state_21_st16(object, 0x176U, 0U);
        recovered_state_21_st16(object, 0x17eU, 0U);
        recovered_state_21_st16(object, 0x17aU, 0U);
        recovered_state_21_st16(object, 0x17cU, 0U);
        recovered_state_21_st16(object, 0x178U, 0U);
        recovered_state_21_st16(object, 0x180U, 0U);
        recovered_state_21_st32(object, 0x190U,
            recovered_state_21_cfg_u32(cfg, 0x664U));
        recovered_state_21_st32(object, 0x1c4U, 0U);
        return;
    }

    /* 0x3223c-0x322f0: the +0x180 sub-phase selects the movement mode and
     * returns to states 0/1. */
    sub = recovered_state_21_ld16(object, 0x180U);
    if (sub == 10U) {                                       /* 0x32244 */
        recovered_state_21_st16(object, 0x170U, 2U);
        recovered_state_21_st16(object, 0x172U, 0U);
        recovered_state_21_st16(object, 0x17cU, 0U);
        recovered_state_21_st16(object, 0x178U, 0U);
        recovered_state_21_st16(object, 0x17aU, 0U);
        recovered_state_21_st16(object, 0x174U, 0U);
        recovered_state_21_st16(object, 0x176U, 0U);
        recovered_state_21_st16(object, 0x17eU, 0U);
        recovered_state_21_st32(object, 0x190U,
            recovered_state_21_cfg_u32(cfg, 0x664U));
    } else if (sub == 11U) {                                /* 0x32280 */
        recovered_state_21_st16(object, 0x170U, 3U);
        recovered_state_21_st16(object, 0x172U, 0U);
        recovered_state_21_st16(object, 0x17cU, 0U);
        recovered_state_21_st16(object, 0x178U, 0U);
        recovered_state_21_st16(object, 0x17aU, 0U);
        recovered_state_21_st16(object, 0x174U, 0U);
        recovered_state_21_st16(object, 0x176U, 0U);
        recovered_state_21_st16(object, 0x17eU, 0U);
        recovered_state_21_st32(object, 0x190U,
            recovered_state_21_cfg_u32(cfg, 0x664U));
    } else if (sub == 12U) {                                /* 0x322bc */
        recovered_state_21_st16(object, 0x172U, 1U);
        recovered_state_21_st16(object, 0x170U, 0U);
        recovered_state_21_st16(object, 0x178U, 0U);
        recovered_state_21_st16(object, 0x17aU, 0U);
        recovered_state_21_st16(object, 0x174U, 0U);
        recovered_state_21_st16(object, 0x17cU, 0U);
        recovered_state_21_st16(object, 0x176U, 0U);
        recovered_state_21_st16(object, 0x17eU, 0U);
        recovered_state_21_st32(object, 0x190U,
            recovered_state_21_cfg_u32(cfg, 0x664U));
    } else {                                                /* 0x322f0 */
        recovered_state_21_st16(object, 0x172U, 0U);
        recovered_state_21_st16(object, 0x170U, 1U);
        recovered_state_21_st32(object, 0x194U, 0U);
        recovered_state_21_st16(object, 0x178U, 0U);
        recovered_state_21_st16(object, 0x17aU, 0U);
        recovered_state_21_st32(object, 0x190U,
            recovered_state_21_cfg_u32(cfg, 0x668U));
    }

    /* 0x32318-0x3231c: clear the sub-phase and the cruise speed. */
    recovered_state_21_st16(object, 0x180U, 0U);
    recovered_state_21_st32(object, 0x1c4U, 0U);
}

/* Absolute-global entry, 0x32120. */
static volatile u32 recovered_state_21_shadow_lo;
static volatile u32 recovered_state_21_shadow_hi;
static volatile u16 recovered_state_21_counter_a;
static volatile u16 recovered_state_21_counter_b;

void recovered_state_21_run(volatile unsigned char *object)
{
    struct recovered_state_21_context ctx;

    ctx.shadow_lo = &recovered_state_21_shadow_lo;
    ctx.shadow_hi = &recovered_state_21_shadow_hi;
    ctx.counter_a = &recovered_state_21_counter_a;
    ctx.counter_b = &recovered_state_21_counter_b;

    recovered_state_21_core(object, &ctx);
}
