/* Bounded, freestanding, runnable recovery of the i960 per-object input
 * consumer / action translation at the head of the 0x25040 sibling update.
 *
 * Provenance
 * ----------
 * The standalone commit body 0x72ea0-0x73480 (recovered separately in
 * recovered_input_commit_run_72ea0.c) produces the latched action bytes at
 * object+0x136 / object+0x137. The sibling per-object update 0x25040-0x26974
 * opens by consuming the raw controller words:
 *
 *   0x2504c-0x25058   [0x50249c] -> object+0xec   (word A, "MA" lane)
 *   0x2505c-0x2506c   [0x5024a4] -> object+0xf0   (word B, "MB" lane)
 *
 * object+0xec is the input substructure base "in"; the listing addresses it
 * through r14/r15 = object+0xec, so every field below is an in-relative offset
 * (the recovered 0x72ea0 body calls the same base g7 = object+0xec). The
 * substructure carries:
 *
 *   in+0x00  word A (u32)          in+0x04  word B (u32)
 *   in+0x1a  object+0x106 command shadow (u16)
 *   in+0x1c  object+0x108 command code (u16)
 *   in+0x4a  object+0x136 action selector (u8)
 *   in+0x4b  object+0x137 committed/latched action (u8)
 *   in+0x4c..+0x57 object+0x138..0x143 repeat/held/edge counters (u8)
 *
 * This unit models, keyed to the listing:
 *
 *   R 0x24f90-0x25038  the per-object reset that seeds object+0x136 = 0xff
 *                      (0x24fc0) and object+0x137 = 0xff (0x24fc4), zeroes the
 *                      counter bytes and clears the two 8-word integrator
 *                      arrays at in+0x28 / in+0x38.
 *   H 0x25040-0x25360  the consumer head: raw word capture, the object+0x108
 *                      command decode from the 0x3d70/0x3da0 nibble tables
 *                      (0x25118-0x2515c), and the command-gated object+0x4a /
 *                      object+0x4f / object+0x50 / object+0x102 stores.
 *   C 0x26404-0x266a8  the in+0x4c..+0x57 repeat/held/edge counter machine
 *                      (the 0x26540 and 0x265a4 writer sites).
 *   A 0x266a8-0x268c4  the command tree that maps object+0x108 to in+0x4a
 *                      (object+0x136); identical shape to the recovered
 *                      0x72ea0 arm at 0x7320c-0x733f0.
 *   L 0x268c4-0x26968  the commit gate, the in+0x4a -> in+0x4b latch
 *                      (object+0x137) and the +0x1f0 timer advance.
 *
 * Out of scope and explicitly not modelled: the game==12 / game==20 /
 * object+0x30==1 / object+0x30==5 service calls (0x25088-0x250f0); the
 * config+0x4c8 array integrators (0x251d4-0x25310, 0x25360-0x253a4, 0x25480+);
 * the conditional 0x72ea0 call-and-return route (0x2633c-0x2634c); and the
 * animation timing phase that the recovered 0x72ea0 unit already covers.
 *
 * The +0x1b2 action field the 0x32810 backbone dispatches on is NOT written
 * anywhere in the 0x25040-0x26974 sibling body modelled here (nor in the
 * 0x24f80-0x25038 reset). Its listing writers are 0x2784c, the
 * 0x2e490..0x32fc0 state handlers and 0x35ef4/0x35f00.
 * `recovered_input_consumer_24fc0_translate` therefore records what is certain
 * (object+0x136 / object+0x137) and deliberately leaves object+0x1b2
 * untouched; the command -> +0x1b2 projection is unresolved.
 *
 * Integer-only, no libc, no floats.
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

/* 0x24f80-0x25038 reset body and 0x25040 head share the object+0xec base. */
#define RECOVERED_INPUT_CONSUMER_INPUT_BASE 0xecU

/* Sibling nibble tables 0x3d70 / 0x3da0 (identical 16-entry halfword tables).
 * The little-endian ROM bytes are
 *   ff00 0400 0000 ff00 0600 0500 0700 ff00
 *   0200 0300 0100 ff00 ff00 ff00 ff00 ff00
 * 0x250f4-0x2515c takes table[(wordA >> 12) & 15] << 8 |
 * table[(wordA >> 20) & 15] into object+0x108. */
static const u16 recovered_input_consumer_24fc0_nibble[16] = {
    0x00ffU, 0x0004U, 0x0000U, 0x00ffU,
    0x0006U, 0x0005U, 0x0007U, 0x00ffU,
    0x0002U, 0x0003U, 0x0001U, 0x00ffU,
    0x00ffU, 0x00ffU, 0x00ffU, 0x00ffU
};

/* in+0x4c/+0x53 branch mask 0x26428/0x264c8: word bit 16 ([0x3dc4]). */
#define RECOVERED_INPUT_CONSUMER_MASK_HI 0x00010000U
/* in+0x52/+0x4d/+0x4e branch mask 0x2650c/0x26588: word bit 8 ([0x3d94]). */
#define RECOVERED_INPUT_CONSUMER_MASK_LO 0x00000100U
/* in+0x56 branch mask 0x26604: word bit 9 ([0x3d98]). */
#define RECOVERED_INPUT_CONSUMER_MASK_56 0x00000200U
/* in+0x57 branch mask 0x26658: word bit 17 ([0x3dc8]). */
#define RECOVERED_INPUT_CONSUMER_MASK_57 0x00020000U

/* Sentinel for the command arm that leaves in+0x4a unchanged (0x268c4). */
#define RECOVERED_INPUT_CONSUMER_NO_CHANGE 0xffffffffU

/* 0x266a8-0x268c4 / 0x7320c-0x733f0: nested command-code tree writing in+0x4a.
 * Returns 0..7, or RECOVERED_INPUT_CONSUMER_NO_CHANGE for the fall-through. */
static u32 recovered_input_consumer_24fc0_command_arm(u32 code)
{
    if (code > 0x504U) {                            /* 0x266b4 */
        if (code > 0x706U) {                        /* 0x2676c */
            if (code == 0xff02U)                    /* 0x267cc */
                return 3U;
            if (code > 0xff02U) {                   /* 0x267d0 */
                if (code == 0xff05U)                /* 0x26810 */
                    return 7U;
                if (code > 0xff05U) {               /* 0x26814 */
                    if (code == 0xff06U)            /* 0x2683c */
                        return 6U;
                    if (code == 0xff07U)            /* 0x26848 */
                        return 5U;
                    return RECOVERED_INPUT_CONSUMER_NO_CHANGE;
                }
                if (code == 0xff03U)                /* 0x26820 */
                    return 4U;
                if (code == 0xff04U)                /* 0x2682c */
                    return 1U;
                return RECOVERED_INPUT_CONSUMER_NO_CHANGE;
            }
            if (code == 0x7ffU)                     /* 0x267d8 */
                return 5U;
            if (code > 0x7ffU) {                    /* 0x267dc */
                if (code == 0xff00U)                /* 0x267f4 */
                    return 0U;
                if (code == 0xff01U)                /* 0x26800 */
                    return 2U;
                return RECOVERED_INPUT_CONSUMER_NO_CHANGE;
            }
            if (code == 0x707U)                     /* 0x267e4 */
                return 5U;
            return RECOVERED_INPUT_CONSUMER_NO_CHANGE;
        }
        if (code > 0x704U)                          /* 0x26774 */
            return 6U;                              /* 0x705, 0x706 */
        if (code > 0x607U) {                        /* 0x26780 */
            if (code == 0x6ffU)                     /* 0x267b0 */
                return 6U;
            if (code < 0x6ffU)                      /* 0x267b4 */
                return RECOVERED_INPUT_CONSUMER_NO_CHANGE;
            if (code > 0x701U)                      /* 0x267bc */
                return RECOVERED_INPUT_CONSUMER_NO_CHANGE;
            return 0U;                              /* 0x700, 0x701 */
        }
        if (code > 0x604U)                          /* 0x26788 */
            return 6U;                              /* 0x605..0x607 */
        if (code > 0x507U) {                        /* 0x26790 */
            if (code == 0x5ffU)                     /* 0x267a4 */
                return 7U;
            return RECOVERED_INPUT_CONSUMER_NO_CHANGE;
        }
        if (code > 0x505U)                          /* 0x26798 */
            return 6U;                              /* 0x506, 0x507 */
        return 7U;                                  /* 0x505 */
    }

    if (code > 0x502U)                              /* 0x266bc */
        return 1U;                                  /* 0x503, 0x504 */
    if (code > 0x203U) {                            /* 0x266c4 */
        if (code > 0x305U) {                        /* 0x2671c */
            if (code > 0x405U) {                    /* 0x26748 */
                if (code == 0x4ffU)                 /* 0x26764 */
                    return 1U;
                return RECOVERED_INPUT_CONSUMER_NO_CHANGE;
            }
            if (code > 0x402U)                      /* 0x26750 */
                return 1U;                          /* 0x403..0x405 */
            if (code == 0x3ffU)                     /* 0x26758 */
                return 4U;
            return RECOVERED_INPUT_CONSUMER_NO_CHANGE;
        }
        if (code > 0x303U)                          /* 0x26724 */
            return 1U;                              /* 0x304, 0x305 */
        if (code > 0x302U)                          /* 0x2672c */
            return 4U;                              /* 0x303 */
        if (code > 0x300U)                          /* 0x26734 */
            return 3U;                              /* 0x301, 0x302 */
        if (code == 0x2ffU)                         /* 0x2673c */
            return 3U;
        return RECOVERED_INPUT_CONSUMER_NO_CHANGE;
    }
    if (code > 0x200U)                              /* 0x266cc */
        return 3U;                                  /* 0x201..0x203 */
    if (code > 0x100U) {                            /* 0x266d4 */
        if (code > 0x103U) {                        /* 0x266f4 */
            if (code == 0x107U)                     /* 0x26708 */
                return 0U;
            if (code == 0x1ffU)                     /* 0x26710 */
                return 2U;
            return RECOVERED_INPUT_CONSUMER_NO_CHANGE;
        }
        if (code > 0x101U)                          /* 0x266fc */
            return 3U;                              /* 0x102, 0x103 */
        return 2U;                                  /* 0x101 */
    }
    if (code > 0xfeU)                               /* 0x266dc */
        return 0U;                                  /* 0xff, 0x100 */
    if (code <= 1U)                                 /* 0x266e4 */
        return 0U;
    if (code == 7U)                                 /* 0x266e8 */
        return 0U;
    return RECOVERED_INPUT_CONSUMER_NO_CHANGE;
}

/* 0x25190-0x251c0 / 0x2525c-0x25284 / 0x2528c: repeat-byte hold update.
 * value > 1 decrements; value == 0 reloads to 0xff; value == 1 holds. */
static void recovered_input_consumer_24fc0_hold(volatile unsigned char *field)
{
    u8 value = *field;

    if (value <= 1U) {
        if (value == 0U)
            *field = 0xffU;
    } else {
        *field = (u8)(value - 1U);
    }
}

/* 0x26404-0x266a8: the in+0x4c..+0x57 repeat/held/edge counters. ma is the
 * in+0x00 word (0x50249c) and mb the in+0x04 word (0x5024a4). */
static void recovered_input_consumer_24fc0_debounce(
    volatile unsigned char *in, u32 ma, u32 mb)
{
    if (in[0x4c] != 0U) {                           /* 0x26404-0x26424 */
        in[0x4c] = (u8)(in[0x4c] - 1U);
        if ((ma & RECOVERED_INPUT_CONSUMER_MASK_HI) != 0U &&
            in[0x4c] == 0U)                         /* 0x26428-0x26444 */
            in[0x4c] = 1U;
    }
    if (in[0x4d] != 0U)                             /* 0x26448-0x26464 */
        in[0x4d] = (u8)(in[0x4d] - 1U);
    if (in[0x4e] != 0U)                             /* 0x26468-0x26480 */
        in[0x4e] = (u8)(in[0x4e] - 1U);
    if (in[0x52] > 1U)                              /* 0x26484-0x2649c */
        in[0x52] = (u8)(in[0x52] - 1U);
    if (in[0x53] > 1U)                              /* 0x264a0-0x264b8 */
        in[0x53] = (u8)(in[0x53] - 1U);

    if ((mb & RECOVERED_INPUT_CONSUMER_MASK_HI) != 0U) {  /* 0x264bc-0x264e4 */
        in[0x53] = 0xffU;
        in[0x55] = (u8)(in[0x55] + 1U);
    } else if ((ma & RECOVERED_INPUT_CONSUMER_MASK_HI) == 0U) {
        in[0x4c] = 0U;
        in[0x53] = 0U;
    }

    if ((mb & RECOVERED_INPUT_CONSUMER_MASK_LO) != 0U) {  /* 0x26500-0x2652c */
        in[0x52] = 0xffU;
        in[0x54] = (u8)(in[0x54] + 1U);
    } else if ((ma & RECOVERED_INPUT_CONSUMER_MASK_LO) == 0U) {
        in[0x4d] = 0U;
        in[0x52] = 0U;
    }

    if (in[0x53] > 0xfbU && in[0x52] > 0xfbU) {     /* 0x26548-0x26578 */
        in[0x52] = 0U;
        in[0x53] = 0U;
        in[0x4e] = 0xffU;
    } else if ((ma & RECOVERED_INPUT_CONSUMER_MASK_LO) == 0U) {
        in[0x4e] = 0U;
    }

    if (in[0x53] <= 0xfdU && in[0x53] != 0U) {      /* 0x265a8-0x265d0 */
        in[0x4c] = 0xffU;
        in[0x53] = 0U;
    }
    if (in[0x52] <= 0xfdU && in[0x52] != 0U) {      /* 0x265d4-0x265fc */
        in[0x4d] = 0xffU;
        in[0x52] = 0U;
    }

    if ((mb & RECOVERED_INPUT_CONSUMER_MASK_56) != 0U) {  /* 0x26600-0x26650 */
        in[0x56] = 0xffU;
    } else if ((ma & RECOVERED_INPUT_CONSUMER_MASK_56) != 0U) {
        if (in[0x56] > 1U)
            in[0x56] = (u8)(in[0x56] - 1U);
    } else {
        in[0x56] = 0U;
    }

    if ((mb & RECOVERED_INPUT_CONSUMER_MASK_57) != 0U) {  /* 0x26654-0x266a4 */
        in[0x57] = 0xffU;
    } else if ((ma & RECOVERED_INPUT_CONSUMER_MASK_57) != 0U) {
        if (in[0x57] > 1U)
            in[0x57] = (u8)(in[0x57] - 1U);
    } else {
        in[0x57] = 0U;
    }
}

/* 0x268c4-0x26968: commit gate, in+0x4a -> in+0x4b latch, +0x1f0 advance. */
static void recovered_input_consumer_24fc0_commit(volatile unsigned char *object)
{
    volatile unsigned char *in = object + RECOVERED_INPUT_CONSUMER_INPUT_BASE;
    u32 committed = 0U;

    if (((u32)in[0x57] > 0xeeU || (u32)in[0x56] > 0xeeU) &&
        (u32)(*(volatile u16 *)(in + 0x1a)) == 0xffffU) {
        committed = 1U;                             /* gate A, 0x268c4-0x268f8 */
    } else if (((u32)in[0x57] > 0xf5U || (u32)in[0x56] > 0xf5U) && (
                   (u32)(*(volatile u16 *)(object + 0x172)) == 15U ||
                   (u32)(*(volatile u16 *)(object + 0x172)) == 16U ||
                   (u32)(*(volatile u16 *)(object + 0x172)) == 31U)) {
        committed = 1U;                             /* gate B, 0x268fc-0x26938 */
    }

    if (committed == 0U)
        return;

    in[0x4b] = in[0x4a];                            /* 0x2693c-0x26944 */
    if (in[0x4b] != 0xffU) {                        /* 0x26948-0x26968 */
        u32 config = *(volatile u32 *)(object + 0x6c);
        u32 advance = *(volatile u32 *)(unsigned long)(config + 0x60cU);
        u32 timer = (u32)(*(volatile u16 *)(object + 0x1f0));

        *(volatile u16 *)(object + 0x1f0) = (u16)(timer + advance);
    }
}

/* 0x25040-0x25360: consumer head. Returns the object+0x108 command code. */
static u32 recovered_input_consumer_24fc0_head(
    volatile unsigned char *object, u32 ma, u32 mb)
{
    volatile unsigned char *in = object + RECOVERED_INPUT_CONSUMER_INPUT_BASE;
    u32 command;

    /* 0x2504c-0x2506c: raw controller words land in the substructure. */
    *(volatile u32 *)(in + 0x00) = ma;
    *(volatile u32 *)(in + 0x04) = mb;

    /* 0x25070-0x25080: snapshot the previous command into object+0x106. */
    command = (u32)(*(volatile u16 *)(in + 0x1c));
    *(volatile u16 *)(in + 0x1a) = (u16)command;

    /* 0x25084-0x25114: the object+0x30 route. The game==12 / game==20 arms and
     * the object+0x30==1 / ==5 service calls are external; the pure helper
     * models the object+0x30==6 clear and the default 0x25118 table decode. */
    switch ((u32)(*(volatile u16 *)(object + 0x30))) {
    case 6:                                         /* 0x250f4-0x25114 */
        command = 0xffffU;
        *(volatile u32 *)(in + 0x00) = 0U;
        *(volatile u32 *)(in + 0x04) = 0U;
        break;
    case 1:                                         /* 0x250d4: call 0x72c10 */
    case 5:                                         /* 0x250e4: bal 0xd5a58 */
        break;
    default:                                        /* 0x25118-0x2515c */
        command = (((u32)recovered_input_consumer_24fc0_nibble[
                        (ma >> 12) & 0x0fU] << 8) |
                   (u32)recovered_input_consumer_24fc0_nibble[
                        (ma >> 20) & 0x0fU]) & 0xffffU;
        break;
    }
    *(volatile u16 *)(in + 0x1c) = (u16)command;

    /* 0x25160-0x2532c: command-gated head stores. The config+0x4c8 array
     * integrators (0x251d4-0x25310, 0x25360+) are deliberately skipped. */
    if (command == 0x602U) {
        recovered_input_consumer_24fc0_hold(in + 0x4f);  /* 0x25190-0x251c0 */
        in[0x50] = 0U;                                   /* 0x251d0 */
        in[0x4a] = 0xffU;                                /* 0x25314/0x2531c */
    } else if ((command & 0xffffU) == 0x206U) {
        if (in[0x50] <= 1U) {                            /* 0x2525c-0x2528c */
            if (in[0x50] == 0U) {
                in[0x50] = 0xffU;
                *(volatile u16 *)(in + 0x16) = 0U;       /* object+0x102 */
            }
        } else {
            in[0x50] = (u8)(in[0x50] - 1U);
        }
        in[0x4f] = 0U;                                   /* 0x252a0 */
        in[0x4a] = 0xffU;                                /* fall to 0x25314 */
    } else {
        in[0x50] = 0U;                                   /* 0x25324-0x25328 */
        in[0x4f] = 0U;                                   /* 0x2532c */
    }

    return command;
}

/* 0x24f90-0x25038: per-object input-substructure reset. The 0x24fc0/0x24fc4
 * stores seed object+0x136 / object+0x137 to 0xff. The listing clears
 * object+0x138-0x13c, 0x13e, 0x13f, 0x142, 0x143 but leaves 0x13d, 0x140 and
 * 0x141 alone; that gap is reproduced verbatim. */
void recovered_input_consumer_24fc0_reset(volatile unsigned char *object)
{
    volatile unsigned char *in = object + RECOVERED_INPUT_CONSUMER_INPUT_BASE;
    u32 i;

    *(volatile u16 *)(object + 0x104) = 0xffffU;    /* 0x24fa4 */
    *(volatile u16 *)(object + 0x102) = 0xffffU;    /* 0x24fa8 */
    *(volatile u16 *)(object + 0x106) = 0xffffU;    /* 0x24fb4 */
    *(volatile u16 *)(object + 0x108) = 0xffffU;    /* 0x24fb8 */

    in[0x4a] = 0xffU;                               /* 0x24fc0: object+0x136 */
    in[0x4b] = 0xffU;                               /* 0x24fc4: object+0x137 */

    *(volatile u16 *)(object + 0x10e) = 0U;         /* 0x24fc8 */
    *(volatile u16 *)(object + 0x10c) = 0U;         /* 0x24fcc */
    *(volatile u16 *)(object + 0x10a) = 0U;         /* 0x24fd0 */

    in[0x50] = 0U;                                  /* 0x24fd4: object+0x13c */
    in[0x4e] = 0U;                                  /* 0x24fd8: object+0x13a */
    in[0x4d] = 0U;                                  /* 0x24fdc: object+0x139 */
    in[0x4c] = 0U;                                  /* 0x24fe0: object+0x138 */
    in[0x4f] = 0U;                                  /* 0x24fe4: object+0x13b */
    in[0x53] = 0U;                                  /* 0x24fe8: object+0x13f */
    in[0x52] = 0U;                                  /* 0x24fec: object+0x13e */
    in[0x57] = 0U;                                  /* 0x24ff0: object+0x143 */
    in[0x56] = 0U;                                  /* 0x24ff4: object+0x142 */

    *(volatile u32 *)(object + 0xf0) = 0U;          /* 0x24ff8 */
    *(volatile u32 *)(in + 0x00) = 0U;              /* 0x25000 */
    *(volatile u16 *)(object + 0xfe) = 0U;          /* 0x25004 */
    *(volatile u16 *)(object + 0xfc) = 0U;          /* 0x25008 */
    *(volatile u32 *)(object + 0xf8) = 0U;          /* 0x25010 */
    *(volatile u32 *)(object + 0xf4) = 0U;          /* 0x25018 */

    for (i = 0U; i < 8U; i++) {                     /* 0x2501c-0x25034 */
        *(volatile u16 *)(in + 0x28 + i * 2U) = 0U;
        *(volatile u16 *)(in + 0x38 + i * 2U) = 0U;
    }
}

/* Pure host-testable consumer: capture the raw words, decode the command,
 * advance the repeat/held/edge counters, resolve the command tree into
 * object+0x136, then run the commit gate that latches object+0x137. Returns
 * the decoded object+0x108 command. object+0x1b2 is never written here. */
u32 recovered_input_consumer_24fc0_translate(
    volatile unsigned char *object, u32 ma, u32 mb)
{
    volatile unsigned char *in = object + RECOVERED_INPUT_CONSUMER_INPUT_BASE;
    u32 command = recovered_input_consumer_24fc0_head(object, ma, mb);
    u32 action;

    recovered_input_consumer_24fc0_debounce(in, ma, mb);    /* 0x26404-0x266a8 */

    action = recovered_input_consumer_24fc0_command_arm(command);  /* 0x266a8 */
    if (action != RECOVERED_INPUT_CONSUMER_NO_CHANGE)
        in[0x4a] = (u8)action;                              /* 0x26850-0x268c0 */

    recovered_input_consumer_24fc0_commit(object);          /* 0x268c4-0x26968 */

    /* object+0x1b2 is written only by 0x2784c, 0x2e490..0x32fc0 and 0x35ef4;
     * no instruction in the recovered ranges touches it. Left untouched. */
    return command;
}

/* Original absolute-global entry, 0x25040. Reads the sibling raw controller
 * words [0x50249c] / [0x5024a4] exactly as 0x2504c-0x2506c. The commit's
 * 0x504dac/0x504db0 MA/MB cells are produced by the input service and consumed
 * by the standalone 0x72ea0 body, not by this consumer. */
void recovered_input_consumer_24fc0_run(volatile unsigned char *object)
{
    u32 ma = *(volatile u32 *)(unsigned long)0x0050249cUL;
    u32 mb = *(volatile u32 *)(unsigned long)0x005024a4UL;

    (void)recovered_input_consumer_24fc0_translate(object, ma, mb);
}
