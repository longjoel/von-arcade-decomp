/* Bounded, freestanding, runnable recovery of the i960 gameplay input-commit
 * body at 0x72ea0-0x73480 (the sole callee of the producer at 0x26340).
 *
 * `recovered_input_commit_run_72ea0` mirrors the original entry: it reads the
 * absolute cabinet globals and forwards them to a pure core. The core performs
 * every store the recovered body makes against a caller-owned player object
 * and its input substructure at object+0xec (the listing's g7).
 *
 * Phases, keyed to the listing:
 *   A 0x72ea0-0x72f64  mode/state-gated MA/MB reload + game==12 override
 *   B 0x72f68-0x7300c  signed +0x1f0 action timer, +0x1e0 gate, +0x1e8 scale
 *   C 0x73010-0x7320c  repeat/held/edge counters, 0xfb/0xfd thresholds, chord
 *   D 0x7320c-0x733f0  object+0x108 command tree -> g7+0x4a in {0..7}
 *   E 0x733f0-0x73480  commit gate, g7+0x4a->g7+0x4b latch, timer advance
 *
 * Out of scope, explicitly: the state==20 lookup helpers 0x882a8/0x88318
 * (0x72f14-0x72f44) and the later 0x73490 helper. The wrapper below keeps the
 * original absolute-global ABI; the core is integer-only, no libc, no floats.
 *
 * Compare/branch polarity follows the listing's literal-first convention used
 * across this codebase (e.g. `cmpibge 4,g4` branches when 4 >= g4). Byte
 * counters are unsigned; `ldos`/`ldob` zero-extend and the Phase A record
 * bytes are sign-extended with the `shlo 24`/`shri 24` idiom.
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;

/* 0x72ec0-0x72f04: record stride is ((bit*8)-bit)<<8 = bit*0x700. */
#define RECOVERED_INPUT_COMMIT_STRIDE 0x700U
#define RECOVERED_INPUT_COMMIT_BYTE_A 0x514U
#define RECOVERED_INPUT_COMMIT_BYTE_B 0x515U

/* Sentinel for the command tree arm at 0x733f0 (leave g7+0x4a unchanged). */
#define RECOVERED_INPUT_COMMIT_NO_CHANGE 0xffffffffU

/* 0x7320c-0x733f0: nested command-code comparison tree writing g7+0x4a.
 * Returns 0..7, or RECOVERED_INPUT_COMMIT_NO_CHANGE for the 0x733f0 arm. */
static u32 recovered_input_commit_command_arm(u32 code)
{
    if (code > 0x504U) {                            /* 0x73214 -> 0x732cc */
        if (code > 0x706U) {                        /* 0x732d0 -> 0x73324 */
            if (code == 0xff02U)                    /* 0x7332c */
                return 3U;
            if (code > 0xff02U) {                   /* 0x73330 -> 0x73368 */
                if (code == 0xff05U)                /* 0x73370 */
                    return 7U;
                if (code > 0xff05U) {               /* 0x73374 -> 0x73394 */
                    if (code == 0xff06U)            /* 0x7339c */
                        return 6U;
                    if (code == 0xff07U)            /* 0x733a8 */
                        return 5U;
                    return RECOVERED_INPUT_COMMIT_NO_CHANGE;
                }
                if (code == 0xff03U)                /* 0x73380 */
                    return 4U;
                if (code == 0xff04U)                /* 0x7338c */
                    return 1U;
                return RECOVERED_INPUT_COMMIT_NO_CHANGE;
            }
            if (code == 0x7ffU)                     /* 0x73338 */
                return 5U;
            if (code > 0x7ffU) {                    /* 0x7333c -> 0x7334c */
                if (code == 0xff00U)                /* 0x73354 */
                    return 0U;
                if (code == 0xff01U)                /* 0x73360 */
                    return 2U;
                return RECOVERED_INPUT_COMMIT_NO_CHANGE;
            }
            if (code == 0x707U)                     /* 0x73344 */
                return 5U;
            return RECOVERED_INPUT_COMMIT_NO_CHANGE;
        }
        /* 0x505..0x706 (0x732d4..) */
        if (code > 0x704U)                          /* 0x732d8 -> 0x733b0 */
            return 6U;                              /* 0x705, 0x706 */
        if (code > 0x607U) {                        /* 0x732e0 -> 0x7330c */
            if (code == 0x6ffU)                     /* 0x73310 */
                return 6U;
            if (code < 0x6ffU)                      /* 0x73314 */
                return RECOVERED_INPUT_COMMIT_NO_CHANGE;
            if (code > 0x701U)                      /* 0x7331c */
                return RECOVERED_INPUT_COMMIT_NO_CHANGE;
            return 0U;                              /* 0x73320: 0x700,0x701 */
        }
        if (code > 0x604U)                          /* 0x732e8 -> 0x733b0 */
            return 6U;                              /* 0x605..0x607 */
        if (code > 0x507U) {                        /* 0x732f0 -> 0x73300 */
            if (code == 0x5ffU)                     /* 0x73304 */
                return 7U;
            return RECOVERED_INPUT_COMMIT_NO_CHANGE;
        }
        if (code > 0x505U)                          /* 0x732f8 -> 0x733b0 */
            return 6U;                              /* 0x506, 0x507 */
        return 7U;                                  /* 0x732fc: 0x505 */
    }

    if (code > 0x502U)                              /* 0x7321c -> 0x733d0 */
        return 1U;                                  /* 0x503, 0x504 */
    if (code > 0x203U) {                            /* 0x73224 -> 0x73278 */
        if (code > 0x305U) {                        /* 0x7327c -> 0x732a4 */
            if (code > 0x405U) {                    /* 0x732a8 -> 0x732c0 */
                if (code == 0x4ffU)                 /* 0x732c4 */
                    return 1U;
                return RECOVERED_INPUT_COMMIT_NO_CHANGE;
            }
            if (code > 0x402U)                      /* 0x732b0 -> 0x733d0 */
                return 1U;                          /* 0x403..0x405 */
            if (code == 0x3ffU)                     /* 0x732b8 */
                return 4U;
            return RECOVERED_INPUT_COMMIT_NO_CHANGE;
        }
        if (code > 0x303U)                          /* 0x73284 -> 0x733d0 */
            return 1U;                              /* 0x304, 0x305 */
        if (code > 0x302U)                          /* 0x7328c -> 0x733c8 */
            return 4U;                              /* 0x303 */
        if (code > 0x300U)                          /* 0x73294 -> 0x733c0 */
            return 3U;                              /* 0x301, 0x302 */
        if (code == 0x2ffU)                         /* 0x7329c */
            return 3U;
        return RECOVERED_INPUT_COMMIT_NO_CHANGE;
    }
    if (code > 0x200U)                              /* 0x7322c -> 0x733c0 */
        return 3U;                                  /* 0x201..0x203 */
    if (code > 0x100U) {                            /* 0x73234 -> 0x73250 */
        if (code > 0x103U) {                        /* 0x73254 -> 0x73264 */
            if (code == 0x107U)                     /* 0x73268 */
                return 0U;
            if (code == 0x1ffU)                     /* 0x73270 */
                return 2U;
            return RECOVERED_INPUT_COMMIT_NO_CHANGE;
        }
        if (code > 0x101U)                          /* 0x7325c -> 0x733c0 */
            return 3U;                              /* 0x102, 0x103 */
        return 2U;                                  /* 0x73260: 0x101 */
    }
    if (code > 0xfeU)                               /* 0x7323c -> 0x733d8 */
        return 0U;                                  /* 0xff, 0x100 */
    if (code <= 1U)                                 /* 0x73244: 0, 1 */
        return 0U;
    if (code == 7U)                                 /* 0x73248 */
        return 0U;
    return RECOVERED_INPUT_COMMIT_NO_CHANGE;
}

/* Pure body of 0x72ea0-0x73480. `ma`/`mb` are the 0x504dac/0x504db0 result
 * cells, `record_table` is the 0x5024f0 base, and the scalar globals are
 * supplied by the wrapper. */
void recovered_input_commit_run_72ea0_core(
    volatile unsigned char *object,
    volatile u32 *ma,
    volatile u32 *mb,
    u32 mode_503a08,
    u32 state_5039f4,
    u32 game_503a00,
    u32 port_bit,
    const volatile unsigned char *record_table)
{
    volatile unsigned char *g7 = object + 0xec;
    volatile unsigned char *config;
    u32 p_a;
    u32 p_b;
    u32 code;
    u32 action;
    u32 cap;
    u32 advance;
    u32 timer;
    u32 numerator;
    u16 raw;

    /* Phase A: 0x72ea0-0x72f04. Mode 2 / state 4 selects the active input
     * record and sign-extends its MA/MB bytes into the result cells. */
    if (mode_503a08 == 2U && state_5039f4 == 4U) {
        const volatile unsigned char *record =
            record_table + (port_bit & 1U) * RECOVERED_INPUT_COMMIT_STRIDE;
        *ma = (u32)(s32)(s8)record[RECOVERED_INPUT_COMMIT_BYTE_A];
        *mb = (u32)(s32)(s8)record[RECOVERED_INPUT_COMMIT_BYTE_B];
    }

    /* 0x72f14-0x72f44: the state==20 lookup (0x882a8/0x88318) is a separate
     * unit; its gate is not modelled here. */

    if (game_503a00 == 12U) {                       /* 0x72f50-0x72f64 */
        *mb = 1U;
        *ma = 1U;
    }

    /* Phase B: 0x72f68-0x7300c. Signed action timer counts down while
     * positive, clamps to config+0x610, then derives the +0x1e0 gate and the
     * +0x1e8 0..100 scale. */
    raw = *(volatile u16 *)(object + 0x1f0);
    if ((s16)raw > 0)
        *(volatile u16 *)(object + 0x1f0) = (u16)((s16)raw - 1);

    config = (volatile unsigned char *)(unsigned long)
        (*(volatile u32 *)(object + 0x6c));
    cap = *(volatile u32 *)(config + 0x610);
    advance = *(volatile u32 *)(config + 0x60c);

    timer = (u32)(u16)(*(volatile u16 *)(object + 0x1f0));
    if ((s32)timer > (s32)cap)                      /* cmpible g4,g5 (signed) */
        *(volatile u16 *)(object + 0x1f0) = (u16)cap;

    timer = (u32)(u16)(*(volatile u16 *)(object + 0x1f0));
    *(volatile u8 *)(object + 0x1e0) =
        (u8)((s32)timer > (s32)(cap - advance) ? 0U : 1U); /* cmpi/bg */
    if (cap != 0U) {                                /* original `divi` traps on 0 */
        /* The listing multiplies by 100 in a 32-bit register then uses the
         * signed `divi`; keep the same wrapping numerator and signed divide. */
        numerator = 100U * (cap - timer);
        *(volatile u16 *)(object + 0x1e8) =
            (u16)((s32)numerator / (s32)cap);
    } else {
        *(volatile u16 *)(object + 0x1e8) = 0U;
    }

    /* Phase C: 0x73010-0x7320c. Repeat/held/edge counters at g7+0x4c..0x57. */
    p_a = *ma;                                      /* 0x504dac */
    p_b = *mb;                                      /* 0x504db0 */

    if (g7[0x4c] != 0) {                            /* 0x73010-0x7304c */
        g7[0x4c] = (u8)(g7[0x4c] - 1U);
        if ((p_b & 4U) != 0U && g7[0x4c] == 0)
            g7[0x4c] = 1U;
    }
    if (g7[0x4d] != 0)                              /* 0x7304c-0x73068 */
        g7[0x4d] = (u8)(g7[0x4d] - 1U);
    if (g7[0x4e] != 0)                              /* 0x73068-0x73080 */
        g7[0x4e] = (u8)(g7[0x4e] - 1U);
    if (g7[0x52] > 1)                               /* 0x73080-0x73098 */
        g7[0x52] = (u8)(g7[0x52] - 1U);
    if (g7[0x53] > 1)                               /* 0x73098-0x730b0 */
        g7[0x53] = (u8)(g7[0x53] - 1U);

    if ((p_b & 2U) != 0U) {                         /* 0x730b0-0x730dc */
        g7[0x53] = 0xffU;
        g7[0x55] = (u8)(g7[0x55] + 1U);
    } else if ((p_b & 4U) == 0U) {
        g7[0x4c] = 0U;
        g7[0x53] = 0U;
    }

    if ((p_a & 2U) != 0U) {                         /* 0x730dc-0x7310c */
        g7[0x52] = 0xffU;
        g7[0x54] = (u8)(g7[0x54] + 1U);
    } else if ((p_a & 4U) == 0U) {
        g7[0x4d] = 0U;
        g7[0x52] = 0U;
    }

    if (g7[0x53] > 0xfb && g7[0x52] > 0xfb) {       /* 0x7310c-0x7314c */
        g7[0x52] = 0U;
        g7[0x53] = 0U;
        g7[0x4e] = 0xffU;
    } else if ((p_a & 4U) == 0U) {
        g7[0x4e] = 0U;
    }

    if (g7[0x53] <= 0xfd && g7[0x53] != 0) {        /* 0x7314c-0x73174 */
        g7[0x4c] = 0xffU;
        g7[0x53] = 0U;
    }
    if (g7[0x52] <= 0xfd && g7[0x52] != 0) {        /* 0x73174-0x7319c */
        g7[0x4d] = 0xffU;
        g7[0x52] = 0U;
    }

    if ((p_a & 0x10U) != 0U)                        /* 0x7319c-0x731d4 */
        g7[0x56] = 0xffU;
    else if ((p_a & 0x20U) != 0U) {
        if (g7[0x56] > 1)
            g7[0x56] = (u8)(g7[0x56] - 1U);
    } else {
        g7[0x56] = 0U;
    }

    if ((p_b & 0x10U) != 0U)                        /* 0x731d4-0x7320c */
        g7[0x57] = 0xffU;
    else if ((p_b & 0x20U) != 0U) {
        if (g7[0x57] > 1)
            g7[0x57] = (u8)(g7[0x57] - 1U);
    } else {
        g7[0x57] = 0U;
    }

    /* Phase D: 0x7320c-0x733f0. Command code at object+0x108. */
    code = (u32)(u16)(*(volatile u16 *)(g7 + 0x1c));
    action = recovered_input_commit_command_arm(code);
    if (action != RECOVERED_INPUT_COMMIT_NO_CHANGE)
        g7[0x4a] = (u8)action;

    /* Phase E: 0x733f0-0x73480. Commit gate, latch, and timer advance. */
    if (((g7[0x57] > 0xee) || (g7[0x56] > 0xee)) &&
        (u32)(u16)(*(volatile u16 *)(g7 + 0x1a)) == 0xffffU) {
        /* gate A: 0x733f0-0x7341c */
    } else if (((g7[0x57] > 0xf5) || (g7[0x56] > 0xf5)) && (
                   (u32)(u16)(*(volatile u16 *)(object + 0x172)) == 15U ||
                   (u32)(u16)(*(volatile u16 *)(object + 0x172)) == 16U ||
                   (u32)(u16)(*(volatile u16 *)(object + 0x172)) == 31U)) {
        /* gate B: 0x73420-0x73454 */
    } else {
        return;
    }

    g7[0x4b] = g7[0x4a];                            /* 0x73458-0x7345c */
    if (g7[0x4b] != 0xff) {                         /* 0x73460-0x73468 */
        *(volatile u16 *)(object + 0x1f0) =
            (u16)(*(volatile u16 *)(object + 0x1f0) + advance);
    }
}

/* Original absolute-global entry, 0x72ea0. Kept as a thin shim so the pure
 * core above can be exercised by the host test without touching 32-bit
 * cabinet memory. */
void recovered_input_commit_run_72ea0(volatile unsigned char *object)
{
    recovered_input_commit_run_72ea0_core(
        object,
        (volatile u32 *)(unsigned long)0x00504dacUL,
        (volatile u32 *)(unsigned long)0x00504db0UL,
        *(volatile u32 *)(unsigned long)0x00503a08UL,
        *(volatile u32 *)(unsigned long)0x005039f4UL,
        *(volatile u32 *)(unsigned long)0x00503a00UL,
        (u32)(*(volatile u8 *)(unsigned long)0x01a14002UL) & 1U,
        (const volatile unsigned char *)(unsigned long)0x005024f0UL);
}
