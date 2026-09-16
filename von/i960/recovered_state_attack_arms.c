/*
 * Bounded freestanding runnable recovered-C unit for the i960 object state
 * handlers 2..9 and 11.  Listing spans in von/build/disasm/vonj-maincpu.lst:
 *
 *   2  0x2e450-0x2e588   3  0x2e590-0x2e6e4   4  0x2e6f0-0x2e854
 *   5  0x2e860-0x2e988   6  0x2e990-0x2ea9c   7  0x2eaa0-0x2ebac
 *   8  0x2ebb0-0x2ecd8   9  0x2ece0-0x2ef80  11  0x2f010-0x2f258
 *
 * The 43-entry 0x32560 update table keys these on object+0x172; the table words
 * at 0x32580, 0x32590, 0x325a0, 0x325b0, 0x325c0, 0x325d0, 0x325e0, 0x325f0
 * and 0x32610 point at the nine addresses above.
 *
 * Shared attack shape (states 2..9)
 *   0x2e450-0x2e478 style preface: when +0x17a == 0 the handler clears +0x1db
 *   and, for states 2..4, seeds +0x17e from +0xa0 (1 when +0xa0 == 0, else 0);
 *   states 5..9 clear +0x1db only.  When +0x17e == 0 and +0x17a == 0 the action
 *   field +0x1b2 is written with 11.  FIFO packet 31 (self x, related x, 0, 0,
 *   self z, related z) is emitted to 0x884000, the projection response is read
 *   back and, when it is negative or +0x17a > 0x30, +0x17e is bumped to retry.
 *   +0x1c4 receives cfg+0x59c (states 2/6/7/9), the +0x64 alternate cfg+0x59c
 *   /0x5a0 (states 3/5/8) or cfg+0x5a4 (state 4); +0x19c = 1 and +0x1af = 3.
 *   States 2..4 clear +0x1aa only when +0x17a > 0x14, states 5..8 clear it
 *   unconditionally.  States 2..8 call the cfg callback at cfg+0x3e4..0x3fc
 *   (state 2 0x3e4, 3 0x3e8, 4 0x3ec, 5 0x3f0, 6 0x3f4, 7 0x3f8, 8 0x3fc)
 *   and then, while +0x17e == 0 and +0x1b4 != 0, bump +0x17e and zero +0x1c4.
 *
 * State 9 (0x2ece0)
 *   Adds the +0x34/+0x184/+0x2e facing half-slew, then after packet 31 and the
 *   +0x1c4/+0x19c/+0x1af arming selects a clip record pair from
 *   cfg+0x1d8/0x1dc (when bit 15 of +0x176 is set or +0x176 > 3) or from
 *   cfg+0x1e0/0x1e4, publishes them at 0x51ab0c/0x51ab08 and, on clip end,
 *   commits +0x172 = 3 for +0x174 1 or 3, else +0x172 = 2, with +0x17a = 21,
 *   +0x17e = +0x176 = +0x180 = 0 and +0x1db = 0.  State 9 has no cfg callback
 *   and does not touch +0x1aa.
 *
 * State 11 (0x2f010)
 *   Runs the same facing half-slew and a three-phase clip machine that
 *   publishes cfg+0x350/0x354, cfg+0x358/0x35c and cfg+0x360/0x364 at
 *   0x51ab0c/0x51ab08.  Clip end in phase 0 advances +0x17e to 1; in phase 1
 *   it selects +0x172 = 12 (+0x180 == 7), 13 (+0x180 == 8) or, on the
 *   +0x13b/+0x1de/+0x1dd/+0x1df sentinel gate, advances to +0x17e = 2; in
 *   phase 2 it commits +0x172 = 0 and +0x170 = 1 (with +0x194 = +0x178 = 0).
 *   State 11 never writes +0x1b2, +0x19c, +0x1af, +0x1db or +0x1c4.
 *
 * Config pointer
 *   st g6,0x6c(g0) at 0x27558 seeds object+0x6c.  The listing reads the same
 *   block through the absolute slot 0x51ab14 (ld 0x51ab14,g4 at 0x2e520,
 *   0x2e558, 0x2e660, 0x2e824, 0x2ea48, 0x2eb58, 0x2ec68, 0x2ef?? and
 *   0x2f05c, 0x2f0dc, 0x2f1c0); this unit reads object+0x6c so it stays
 *   freestanding and host-testable.  The absolute publication cells
 *   0x51ab08/0x51ab0c (record-pointer scratch) and 0x51ab10/0x51ab12
 *   (write-only counters) are file-static stand-ins, as is the 0x884000 cell.
 *
 * Projection response
 *   The live 0x884000 exchange is external board behaviour.  The 0x32810
 *   per-object prefix (recovered_object_update_prefix_32810.c) caches the
 *   opcode-31 response at object+0x7c and the opcode-10 response at object+0x84
 *   (the 0x6f6f0-family projection result lands there).  The bounded model
 *   consumes the packet-31 word at object+0x7c, and the cfg callbacks at
 *   cfg+0x3e4..0x3fc are the same external boundary.
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef short s16;
typedef int s32;

/* 0x27558/0x2e520: the config pointer lives at object+0x6c. */
#define RECOVERED_STATE_ATTACK_CONFIG_OFFSET 0x6cU

/* 0x2e498/0x2ed4c/0x2ee14...: the absolute config slot and FIFO the listing
 * uses; only the FIFO has a stand-in cell here (the config is read through
 * object+0x6c). */
#define RECOVERED_STATE_ATTACK_CONFIG_SLOT 0x0051ab14U
#define RECOVERED_STATE_ATTACK_FIFO 0x00884000U

/* 0x51ab08/0x51ab0c/0x51ab10/0x51ab12: absolute scratch stand-ins. */
static volatile u32 recovered_state_attack_fifo;         /* 0x884000 */
static volatile u32 recovered_state_attack_publish_lo;   /* 0x51ab08 */
static volatile u32 recovered_state_attack_publish_hi;   /* 0x51ab0c */
static volatile u16 recovered_state_attack_counter_a;    /* 0x51ab10 */
static volatile u16 recovered_state_attack_counter_b;    /* 0x51ab12 */

static volatile unsigned char *recovered_state_attack_config(
    volatile unsigned char *object)
{
    return (volatile unsigned char *)(unsigned long)
        *(volatile u32 *)(object + RECOVERED_STATE_ATTACK_CONFIG_OFFSET);
}

static u32 recovered_state_attack_ld32(const volatile unsigned char *object,
                                       u32 offset)
{
    return *(const volatile u32 *)(object + offset);
}

static u16 recovered_state_attack_ldos(const volatile unsigned char *object,
                                       u32 offset)
{
    return *(const volatile u16 *)(object + offset);
}

static u8 recovered_state_attack_ldob(const volatile unsigned char *object,
                                      u32 offset)
{
    return *(const volatile u8 *)(object + offset);
}

static void recovered_state_attack_st32(volatile unsigned char *object,
                                        u32 offset, u32 value)
{
    *(volatile u32 *)(object + offset) = value;
}

static void recovered_state_attack_stos(volatile unsigned char *object,
                                        u32 offset, u32 value)
{
    *(volatile u16 *)(object + offset) = (u16)value;
}

static void recovered_state_attack_stob(volatile unsigned char *object,
                                        u32 offset, u32 value)
{
    *(volatile u8 *)(object + offset) = (u8)value;
}

static u32 recovered_state_attack_cfg_u32(const volatile unsigned char *cfg,
                                          u32 offset)
{
    return *(const volatile u32 *)(cfg + offset);
}

/*
 * The external 0x884000 response.  0x32810 caches the opcode-31 projection
 * response at object+0x7c and the opcode-10 response at object+0x84; the
 * handle below reads the packet-31 word so the attack body stays runnable.
 */
static float recovered_state_attack_cached_response(
    const volatile unsigned char *object)
{
    union {
        u32 bits;
        float value;
    } raw;

    raw.bits = *(const volatile u32 *)(object + 0x7cU);
    return raw.value;
}

/*
 * 0x2e494-0x2e4ec (states 2..8) and 0x2ed48-0x2edb8 (state 9).  The six
 * payload words are self x (+0x8), related x (+0xa4), 0, 0, self z (+0x10)
 * and related z (+0xa8); the board response is the external projection, read
 * here from the cached object+0x7c word.
 */
static float recovered_state_attack_packet31(volatile unsigned char *object)
{
    u32 self_x = recovered_state_attack_ld32(object, 0x08U);
    u32 self_z = recovered_state_attack_ld32(object, 0x10U);
    u32 rel_x = recovered_state_attack_ld32(object, 0xa4U);
    u32 rel_z = recovered_state_attack_ld32(object, 0xa8U);
    u32 echo;

    recovered_state_attack_fifo = 31U;
    recovered_state_attack_fifo = self_x;
    recovered_state_attack_fifo = rel_x;
    recovered_state_attack_fifo = 0U;
    recovered_state_attack_fifo = 0U;
    recovered_state_attack_fifo = self_z;
    recovered_state_attack_fifo = rel_z;
    echo = recovered_state_attack_fifo;
    (void)echo;
    return recovered_state_attack_cached_response(object);
}

/*
 * Shared body of states 2..9 (e.g. 0x2e47c-0x2e53c).  Packet 31, the
 * negative-response / +0x17a > 0x30 retry, the +0x1c4 speed store and the
 * +0x19c/+0x1af arming.  `speed_bits` is the cfg word the caller selected.
 */
static void recovered_state_attack_body(volatile unsigned char *object,
                                        u32 speed_bits)
{
    float response;

    if (recovered_state_attack_ldos(object, 0x17eU) != 0U)
        return;

    if (recovered_state_attack_ldos(object, 0x17aU) == 0U)
        recovered_state_attack_stos(object, 0x1b2U, 11U);

    response = recovered_state_attack_packet31(object);
    if (response < 0.0f
        || (((u32)recovered_state_attack_ldos(object, 0x17aU) << 16)
            > 0x300000U))
        recovered_state_attack_stos(
            object, 0x17eU,
            (u32)recovered_state_attack_ldos(object, 0x17eU) + 1U);

    recovered_state_attack_st32(object, 0x1c4U, speed_bits);
    recovered_state_attack_stos(object, 0x19cU, 1U);
    recovered_state_attack_stob(object, 0x1afU, 3U);
}

/* 0x2e450-0x2e478 (states 2/3/4): +0x1db = 0 and +0x17e seeded from +0xa0. */
static void recovered_state_attack_seed_phase(volatile unsigned char *object)
{
    if (recovered_state_attack_ldos(object, 0x17aU) != 0U)
        return;
    recovered_state_attack_stob(object, 0x1dbU, 0U);
    recovered_state_attack_stos(
        object, 0x17eU,
        (recovered_state_attack_ldob(object, 0xa0U) == 0U) ? 1U : 0U);
}

/* 0x2e860-0x2e870 (states 5..9): only +0x1db = 0 is cleared. */
static void recovered_state_attack_seed_flag(volatile unsigned char *object)
{
    if (recovered_state_attack_ldos(object, 0x17aU) == 0U)
        recovered_state_attack_stob(object, 0x1dbU, 0U);
}

/* 0x2e540-0x2e554 (states 2/3/4): +0x1aa = 0 only when +0x17a > 0x14. */
static void recovered_state_attack_gate_1aa(volatile unsigned char *object)
{
    if ((((u32)recovered_state_attack_ldos(object, 0x17aU) << 16)
         > 0x140000U))
        recovered_state_attack_stob(object, 0x1aaU, 0U);
}

/* 0x2e954/0x2ea68/0x2eb78/0x2eca4 (states 5..8): unconditional clear. */
static void recovered_state_attack_clear_1aa(volatile unsigned char *object)
{
    recovered_state_attack_stob(object, 0x1aaU, 0U);
}

/*
 * Shared callback + phase tail.  0x2e558-0x2e588 (states 2..8) loads the cfg
 * callback at cfg+0x3e4..0x3fc, calls it, then, while +0x17e == 0 and
 * +0x1b4 != 0, bumps +0x17e and zeroes +0x1c4.  The callback is external, so
 * only a non-zero pointer is invoked; callback_offset == 0 is state 9, which
 * has no callback at 0x2ef5c-0x2ef7c.
 */
static void recovered_state_attack_finish(volatile unsigned char *object,
                                          u32 callback_offset)
{
    if (callback_offset != 0U) {
        volatile unsigned char *cfg = recovered_state_attack_config(object);
        u32 callback = recovered_state_attack_cfg_u32(cfg, callback_offset);

        (void)recovered_state_attack_cached_response(object);
        if (callback != 0U)
            ((void (*)(volatile unsigned char *))(unsigned long)callback)(
                object);
    }

    if (recovered_state_attack_ldos(object, 0x17eU) != 0U)
        return;
    if (recovered_state_attack_ld32(object, 0x1b4U) == 0U)
        return;
    recovered_state_attack_stos(
        object, 0x17eU,
        (u32)recovered_state_attack_ldos(object, 0x17eU) + 1U);
    recovered_state_attack_st32(object, 0x1c4U, 0U);
}

/*
 * 0x2e660-0x2e688 (states 3/5/8): +0x64 is 0 or 1 -> cfg+0x59c, else
 * cfg+0x5a0.
 */
static u32 recovered_state_attack_speed_alt(
    const volatile unsigned char *object, const volatile unsigned char *cfg)
{
    u32 selector = recovered_state_attack_ld32(object, 0x64U);

    if (selector == 0U || selector == 1U)
        return recovered_state_attack_cfg_u32(cfg, 0x59cU);
    return recovered_state_attack_cfg_u32(cfg, 0x5a0U);
}

/*
 * 0x2ecf8-0x2ed20 (state 9) and 0x2f028-0x2f050 (state 11): the facing
 * half-slew.  delta = (s16)(+0x34 + +0x184 - +0x2e); +0x2e += delta >> 1
 * (the shlo 16 / shri 16 sign-extension then shrdi 1 arithmetic halving).
 */
static void recovered_state_attack_facing_slew(volatile unsigned char *object)
{
    u32 current = (u32)recovered_state_attack_ldos(object, 0x2eU);
    u32 raw = (u32)recovered_state_attack_ldos(object, 0x34U)
            + (u32)recovered_state_attack_ldos(object, 0x184U)
            - current;
    s32 delta = (s32)(s16)(u16)raw;

    delta >>= 1;
    recovered_state_attack_stos(object, 0x2eU, current + (u32)delta);
}

void recovered_state_attack_2_run(volatile unsigned char *object)
{
    volatile unsigned char *cfg = recovered_state_attack_config(object);

    recovered_state_attack_seed_phase(object);
    recovered_state_attack_body(object,
                                recovered_state_attack_cfg_u32(cfg, 0x59cU));
    recovered_state_attack_gate_1aa(object);
    recovered_state_attack_finish(object, 0x3e4U);
}

void recovered_state_attack_3_run(volatile unsigned char *object)
{
    volatile unsigned char *cfg = recovered_state_attack_config(object);

    recovered_state_attack_seed_phase(object);
    recovered_state_attack_body(object,
                                recovered_state_attack_speed_alt(object, cfg));
    recovered_state_attack_gate_1aa(object);
    recovered_state_attack_finish(object, 0x3e8U);
}

void recovered_state_attack_4_run(volatile unsigned char *object)
{
    volatile unsigned char *cfg = recovered_state_attack_config(object);

    recovered_state_attack_seed_phase(object);
    recovered_state_attack_body(object,
                                recovered_state_attack_cfg_u32(cfg, 0x5a4U));
    recovered_state_attack_gate_1aa(object);
    recovered_state_attack_finish(object, 0x3ecU);
}

void recovered_state_attack_5_run(volatile unsigned char *object)
{
    volatile unsigned char *cfg = recovered_state_attack_config(object);

    recovered_state_attack_seed_flag(object);
    recovered_state_attack_body(object,
                                recovered_state_attack_speed_alt(object, cfg));
    recovered_state_attack_clear_1aa(object);
    recovered_state_attack_finish(object, 0x3f0U);
}

void recovered_state_attack_6_run(volatile unsigned char *object)
{
    volatile unsigned char *cfg = recovered_state_attack_config(object);

    recovered_state_attack_seed_flag(object);
    recovered_state_attack_body(object,
                                recovered_state_attack_cfg_u32(cfg, 0x59cU));
    recovered_state_attack_clear_1aa(object);
    recovered_state_attack_finish(object, 0x3f4U);
}

void recovered_state_attack_7_run(volatile unsigned char *object)
{
    volatile unsigned char *cfg = recovered_state_attack_config(object);

    recovered_state_attack_seed_flag(object);
    recovered_state_attack_body(object,
                                recovered_state_attack_cfg_u32(cfg, 0x59cU));
    recovered_state_attack_clear_1aa(object);
    recovered_state_attack_finish(object, 0x3f8U);
}

void recovered_state_attack_8_run(volatile unsigned char *object)
{
    volatile unsigned char *cfg = recovered_state_attack_config(object);

    recovered_state_attack_seed_flag(object);
    recovered_state_attack_body(object,
                                recovered_state_attack_speed_alt(object, cfg));
    recovered_state_attack_clear_1aa(object);
    recovered_state_attack_finish(object, 0x3fcU);
}

void recovered_state_attack_9_run(volatile unsigned char *object)
{
    volatile unsigned char *cfg = recovered_state_attack_config(object);
    volatile unsigned char *record;
    u32 f174;
    u32 f176;
    u32 index;
    u32 count;

    /* 0x2ecf0/0x2ecf4: +0x186 = +0x188 = 0; 0x2ecf8-0x2ed20: facing slew. */
    recovered_state_attack_stos(object, 0x186U, 0U);
    recovered_state_attack_stos(object, 0x188U, 0U);
    recovered_state_attack_facing_slew(object);

    /* 0x2ed24-0x2ed30: +0x1db = 0 when +0x17a == 0. */
    recovered_state_attack_seed_flag(object);

    /* 0x2ed30-0x2edf0: packet 31, retry, +0x1c4 / +0x19c / +0x1af. */
    recovered_state_attack_body(object,
                                recovered_state_attack_cfg_u32(cfg, 0x59cU));

    /* 0x2edf4-0x2eea4: record pair from cfg+0x1d8/0x1dc or cfg+0x1e0/0x1e4. */
    f174 = (u32)recovered_state_attack_ldos(object, 0x174U);
    f176 = (u32)recovered_state_attack_ldos(object, 0x176U);
    if ((f176 & 0x8000U) != 0U
        || ((s32)((u32)f176 << 16) > (s32)0x30000)) {
        index = f174 * 40U;
        recovered_state_attack_publish_hi =
            recovered_state_attack_cfg_u32(cfg, 0x1d8U + index);
        record = (volatile unsigned char *)(unsigned long)
            recovered_state_attack_cfg_u32(cfg, 0x1dcU + index);
    } else {
        index = f174 * 40U + ((u32)f176 << 3);
        recovered_state_attack_publish_hi =
            recovered_state_attack_cfg_u32(cfg, 0x1e0U + index);
        record = (volatile unsigned char *)(unsigned long)
            recovered_state_attack_cfg_u32(cfg, 0x1e4U + index);
    }
    recovered_state_attack_publish_lo = (u32)(unsigned long)record;

    /* 0x2eeb8-0x2ef38: clip end -> +0x172 = 3 for +0x174 1/3 else 2. */
    count = (u32)recovered_state_attack_ldos(record, 0x4U);
    if ((s32)(u32)recovered_state_attack_ldos(object, 0x17aU)
            < (s32)(count - 1U)) {
        u32 old = (u32)recovered_state_attack_ldos(object, 0x17aU);

        recovered_state_attack_counter_b = (u16)old;
        recovered_state_attack_stos(object, 0x17aU, old + 1U);
        recovered_state_attack_counter_a = (u16)old;
    } else {
        u32 selector = (u32)recovered_state_attack_ldos(object, 0x174U);

        recovered_state_attack_counter_b = (u16)(count - 1U);
        recovered_state_attack_counter_a = (u16)(count - 1U);
        if (selector == 3U || selector == 1U)
            recovered_state_attack_stos(object, 0x172U, 3U);
        else
            recovered_state_attack_stos(object, 0x172U, 2U);
        recovered_state_attack_stos(object, 0x17aU, 21U);
        recovered_state_attack_stos(object, 0x17eU, 0U);
        recovered_state_attack_stos(object, 0x176U, 0U);
        recovered_state_attack_stos(object, 0x180U, 0U);
        recovered_state_attack_stob(object, 0x1dbU, 0U);
    }

    /* 0x2ef5c-0x2ef7c: shared phase tail; state 9 has no cfg callback. */
    recovered_state_attack_finish(object, 0U);
}

void recovered_state_attack_11_run(volatile unsigned char *object)
{
    volatile unsigned char *cfg = recovered_state_attack_config(object);
    volatile unsigned char *record;
    u32 phase;
    u32 f17a;
    u32 count;

    /* 0x2f020/0x2f024: +0x186 = +0x188 = 0; 0x2f028-0x2f050: facing slew. */
    recovered_state_attack_stos(object, 0x186U, 0U);
    recovered_state_attack_stos(object, 0x188U, 0U);
    recovered_state_attack_facing_slew(object);

    phase = (u32)recovered_state_attack_ldos(object, 0x17eU);

    if (phase == 0U) {
        /* 0x2f05c-0x2f09c: cfg+0x350/0x354; increment while +0x17a < count-1. */
        record = (volatile unsigned char *)(unsigned long)
            recovered_state_attack_cfg_u32(cfg, 0x354U);
        recovered_state_attack_publish_hi =
            recovered_state_attack_cfg_u32(cfg, 0x350U);
        recovered_state_attack_publish_lo = (u32)(unsigned long)record;

        count = (u32)recovered_state_attack_ldos(record, 0x4U);
        f17a = (u32)recovered_state_attack_ldos(object, 0x17aU);
        if ((s32)f17a < (s32)(count - 1U)) {
            recovered_state_attack_counter_b = (u16)f17a;
            recovered_state_attack_stos(object, 0x17aU, f17a + 1U);
            recovered_state_attack_counter_a = (u16)f17a;
        } else {
            /* 0x2f0a0-0x2f0bc: clip end advances to phase 1. */
            recovered_state_attack_stos(object, 0x17eU, 1U);
            recovered_state_attack_stos(object, 0x17aU, 0U);
            recovered_state_attack_counter_b = (u16)(count - 1U);
            recovered_state_attack_counter_a = (u16)(count - 1U);
        }
        recovered_state_attack_clear_1aa(object);        /* 0x2f130-0x2f138 */
    } else if (phase == 1U) {
        /* 0x2f0dc-0x2f118: cfg+0x358/0x35c; increment while +0x17a < count. */
        record = (volatile unsigned char *)(unsigned long)
            recovered_state_attack_cfg_u32(cfg, 0x35cU);
        recovered_state_attack_publish_hi =
            recovered_state_attack_cfg_u32(cfg, 0x358U);
        recovered_state_attack_publish_lo = (u32)(unsigned long)record;

        count = (u32)recovered_state_attack_ldos(record, 0x4U);
        f17a = (u32)recovered_state_attack_ldos(object, 0x17aU);
        if ((s32)f17a < (s32)count) {
            recovered_state_attack_counter_b = (u16)f17a;
            recovered_state_attack_stos(object, 0x17aU, f17a + 1U);
            recovered_state_attack_counter_a = (u16)f17a;
            recovered_state_attack_clear_1aa(object);    /* 0x2f130-0x2f138 */
        } else {
            u32 f180;

            /* 0x2f140-0x2f184: clip end selects 12/13 by +0x180. */
            count = (u32)recovered_state_attack_ldos(record, 0x4U);
            recovered_state_attack_counter_b = (u16)(count - 1U);
            recovered_state_attack_counter_a = (u16)(count - 1U);
            f180 = (u32)recovered_state_attack_ldos(object, 0x180U);
            if (f180 == 7U) {
                recovered_state_attack_stos(object, 0x172U, 12U);
                recovered_state_attack_stos(object, 0x17eU, 0U);
                recovered_state_attack_stos(object, 0x17aU, 0U);
            } else if (f180 == 8U) {
                recovered_state_attack_stos(object, 0x172U, 13U);
                recovered_state_attack_stos(object, 0x17eU, 0U);
                recovered_state_attack_stos(object, 0x17aU, 0U);
            } else if (recovered_state_attack_ldob(object, 0x13bU) == 0U
                       || (((recovered_state_attack_ldob(object, 0x1deU)
                             & 2U) == 0U)
                           && ((recovered_state_attack_ldob(object, 0x1ddU)
                                & 2U) == 0U)
                           && ((recovered_state_attack_ldob(object, 0x1dfU)
                                & 2U) == 0U))) {
                /* 0x2f188-0x2f1b0: sentinel gate advances to phase 2. */
                recovered_state_attack_stos(object, 0x17eU, 2U);
                recovered_state_attack_stos(object, 0x17aU, 0U);
            }
        }
    } else if (phase == 2U) {
        /* 0x2f1b8-0x2f200: cfg+0x360/0x364; increment while +0x17a < count-1. */
        record = (volatile unsigned char *)(unsigned long)
            recovered_state_attack_cfg_u32(cfg, 0x364U);
        recovered_state_attack_publish_hi =
            recovered_state_attack_cfg_u32(cfg, 0x360U);
        recovered_state_attack_publish_lo = (u32)(unsigned long)record;

        count = (u32)recovered_state_attack_ldos(record, 0x4U);
        f17a = (u32)recovered_state_attack_ldos(object, 0x17aU);
        if ((s32)f17a < (s32)(count - 1U)) {
            recovered_state_attack_counter_b = (u16)f17a;
            recovered_state_attack_stos(object, 0x17aU, f17a + 1U);
            recovered_state_attack_counter_a = (u16)f17a;
        } else {
            /* 0x2f204-0x2f234: clip end commits +0x172 = 0 / +0x170 = 1. */
            recovered_state_attack_stos(object, 0x172U, 0U);
            recovered_state_attack_stos(object, 0x170U, 1U);
            recovered_state_attack_stos(object, 0x194U, 0U);
            recovered_state_attack_stos(object, 0x178U, 0U);
            recovered_state_attack_stos(object, 0x17aU, 0U);
            recovered_state_attack_counter_b = (u16)(count - 1U);
            recovered_state_attack_counter_a = (u16)(count - 1U);
        }
    }
}
