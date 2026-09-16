/*
 * Bounded freestanding runnable recovered-C unit for the i960 locomotion
 * action arms 0 and 12 of the 0x32810 per-object update.  The two arms are
 * reached from the 14-entry jump table at 0x32968 (`ld 0x32968[g4*4],g4` /
 * `bx (g4)` on the masked object+0x1b2 state), which dispatches 0x329c4 for
 * arm 0 and 0x32ea4 for arm 12.
 *
 * The config pointer is object+0x6c (`st g6,0x6c(g0)` seeded by the object
 * initializer 0x27550); the listing's literal is the absolute global
 * 0x51ab14, reproduced only by the _run wrappers below.  All helpers are
 * static, there is no libc, and the two run entry points keep the original
 * `void f(volatile unsigned char *object)` ABI.
 *
 * Arm 0, listing 0x000329c4-0x00032a88:
 *
 *   0x329c4  ldos 0x172(g0),g4
 *   0x329c8  shlo 16,g4,g4
 *   0x329cc  shri 12,g4,g4           (s16)+0x172 * 16: the table word1 index
 *   0x329d0  ld 0x32564(g4),g4       per-state word1 flag (state table word1)
 *   0x329d8  cmpibe 0,g4,0x32a4c     flag == 0 jumps straight to the turn
 *   0x329dc  ldos 0x34(g0),g5
 *   0x329e0  ldos 0x184(g0),g4
 *   0x329e4  ldos 0x2e(g0),g6
 *   0x329e8  shlo 8,3,g7             g7 = 0x300 fixed auto-face slew limit
 *   0x329ec  addo g5,g4,g5           target = +0x184 + +0x34
 *   0x329f0  subo g6,g5,g5           delta = target - +0x2e
 *   0x329f4  shlo 16,g5,g4
 *   0x329f8  shri 16,g4,g4           sign-extend the 16-bit delta
 *   0x329fc  cmpi g7,g4 / bge
 *   0x32a10  lda 0xfffffd00,g5       -0x300 lower bound
 *   0x32a18  cmpibge g4,g5,0x32a20
 *   0x32a20  ldos 0x2e(g0),g4
 *   0x32a24  addo g6,g4,g4
 *   0x32a28  stos g4,0x2e(g0)        +0x2e += clamp(delta, -0x300, 0x300)
 *   0x32a2c  ldos 0x184(g0),g4
 *   0x32a30  ldos 0x10a(g0),g5
 *   0x32a38  stos g4,0x184(g0)       +0x184 += +0x10a
 *   0x32a3c  ldos 0x2e(g0),g4
 *   0x32a40  ldos 0x10a(g0),g5
 *   0x32a48  stos g4,0x2e(g0)        +0x2e += +0x10a
 *   0x32a4c  ld 0x51ab14,g7          config (re-homed to object+0x6c here)
 *   0x32a54  ldos 0x184(g0),g5
 *   0x32a58  ldos 0x1a(g3),g4        g3+0x1a mode target
 *   0x32a5c  ld 0x528(g7),g6         cfg+0x528 turn limit
 *   0x32a60  subo g4,g5,g5           delta = +0x184 - mode_target
 *   0x32a64  shlo 16,g5,g4
 *   0x32a68  shri 16,g4,g1
 *   0x32a6c  cmpi g6,g1 / bl 0x32cc4
 *   0x32a78  ld 0x528(g7),g4
 *   0x32a7c  subo g4,0,g4            -cfg+0x528
 *   0x32a80  cmpibge g1,g4,0x32cec
 *   0x32a84  b 0x32bb4
 *   0x32cec  ldos 0x1a(g3),g4
 *   0x32cf0  addo g6,g4,g4
 *   0x32cf4  stos g4,0x1a(g3)        mode_target += clamp(delta, +/-cfg+0x528)
 *
 * So arm 0 is: with the per-state word1 flag set, slew +0x2e toward
 * (+0x184 + +0x34) by at most 0x300 and add +0x10a to +0x184/+0x2e; the
 * turn tail then carries the (possibly already advanced) +0x184 into the
 * g3+0x1a mode target, clamped by +/-cfg+0x528.  The gate is the value the
 * state table at 0x32560 stores in word1 of each 16-byte entry, read through
 * 0x32564 by arm 0.
 *
 * Arm 12, listing 0x00032ea4-0x00032fd0:
 *
 *   0x32ea4  ld 0xa8(g0),g5          related z cached by the 0x32810 prefix
 *   0x32ea8  ld 0x10(g0),g7          self z
 *   0x32eac  ld 0x8(g0),g4           self x
 *   0x32eb0  ld 0xa4(g0),g6          related x
 *   0x32eb4  mov 10,r10
 *   0x32eb8  subr g6,g4,g4           self x - related x
 *   0x32ebc  st r10,0x884000         opcode 10
 *   0x32ec4  subr g7,g5,g5           related z - self z
 *   0x32ed0  st g5,0x884000
 *   0x32ed8  st g4,0x884000
 *   0x32ee0  ld 0x884000,g5          SHARC projection response
 *   0x32ee8  ldos 0x2e(g0),g4
 *   0x32eec  ld 0x52c(g7),g6         cfg+0x52c snap limit
 *   0x32ef0  subo g4,g5,g5
 *   0x32ef4  shlo 16,g5,g4
 *   0x32ef8  shri 16,g4,g1
 *   0x32efc  cmpi g6,g1 / mov g5,g6 / bl 0x32cc4
 *   0x32f08  ld 0x52c(g7),g4
 *   0x32f0c  ldos 0x2e(g0),g5
 *   0x32f14  stos g4,0x2e(g0)        +0x2e += +cfg+0x52c (high saturation)
 *   0x32f18  ldos 0x19c(g0),g4 / cmpibe 0,g4,0x32fc4
 *   0x32f24  ld 0x52c(g7),g4 / subo g4,0,g4
 *   0x32f2c  cmpibge g1,g4,0x32f70
 *   0x32f38  stos g5,0x2e(g0)        +0x2e -= +cfg+0x52c (low saturation)
 *   0x32f48  ld 0x1c4(g0),g4         saturated rescale path
 *   0x32f54  lda 0x3fe00000,g5
 *   0x32f5c  mulrl fp0,g4,g4
 *   0x32f68  st g4,0x1c4(g0)         +0x1c4 = (float)((double)+0x1c4 * 0.5)
 *   0x32f70  lda 0x400(g5),g4 / lda 0xffff,g5 / and
 *   0x32f80  setbit 11,0,r11         r11 = 0x800
 *   0x32f84  cmpoble g4,r11,0x32fb4  within-limit quadrant half-test
 *   0x32f88  ldos 0x19c(g0),g4 / cmpibe 0,g4,0x32fb4
 *   0x32f9c  lda 0x3fe80000,g5
 *   0x32fa4  mulrl fp0,g4,g4
 *   0x32fb0  st g4,0x1c4(g0)         +0x1c4 = (float)((double)+0x1c4 * 0.75)
 *   0x32fb4  ldos 0x2e(g0),g4 / addo g6,g4,g4
 *   0x32fbc  stos g4,0x2e(g0)        +0x2e += raw response delta
 *   0x32fc0  stos g14,0x1b2(g0)      +0x1b2 = 0
 *   0x32fc4  ldos 0x2e(g0),g4
 *   0x32fc8  stos g4,0x184(g0)       +0x184 = +0x2e
 *   0x32fcc  b 0x33080
 *
 * The opcode-10 packet is the same 0x6f6f0-family projection the 0x32810
 * prefix (recovered_object_update_prefix_32810.c) drives and caches at
 * object+0x7c (opcode 31) / object+0x84 (opcode 10).  The bounded model
 * consumes that cached response at object+0x84 so the unit is runnable
 * without the 0x884000 FIFO; only the low 16 bits of the response survive
 * the listing's shlo/shri pair, so the cached halfword is exact.
 *
 * The two rescale constants are the double high words 0x3fe00000 (0.5) and
 * 0x3fe80000 (0.75) of the g4:g5 pair that `mulrl` consumes; read as bare
 * 32-bit singles they would spell 1.75 / 1.8125, but the opcode is the
 * real-long multiply.
 *
 * The action-12 auto-face stores +0x1b2 only on the within-limit path
 * (0x32fc0); the saturated arms jump from 0x32f1c/0x32f44/0x32f6c directly to
 * the 0x32fc4 commit, so they leave +0x1b2 alone.
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed short s16;
typedef signed int s32;

/* 0x329c4-0x329d0: the state-table word1 flag table entry stride. */
#define RECOVERED_LOCOMOTION_ACTION_STATE_TABLE 0x00032564U

/* Preamble 0x32938/0x32944 select g3 from object+0x30 and 0x32a58/0x32cf4
 * read/write g3+0x1a (the mode target). */
#define RECOVERED_LOCOMOTION_ACTION_MODE_TABLE_NONZERO 0x00504be0U
#define RECOVERED_LOCOMOTION_ACTION_MODE_TABLE_ZERO 0x00504b90U
#define RECOVERED_LOCOMOTION_ACTION_MODE_TARGET_OFFSET 0x1aU

/* 0x32a4c / 0x32eec: the absolute config slot the listing uses. */
#define RECOVERED_LOCOMOTION_ACTION_CONFIG_SLOT 0x0051ab14U

/* 0x32a5c and 0x32eec: the two config words arm 0 and arm 12 read. */
#define RECOVERED_LOCOMOTION_ACTION_TURN_LIMIT 0x528U
#define RECOVERED_LOCOMOTION_ACTION_SNAP_LIMIT 0x52cU

/* 0x329e8 / 0x32a10: the fixed auto-face slew bound (+/-0x300). */
#define RECOVERED_LOCOMOTION_ACTION_SLEW_LIMIT 0x300

/* 0x32ebc/0x32ee0: the SHARC opcode-10 projection FIFO. */
#define RECOVERED_LOCOMOTION_ACTION_FIFO 0x00884000U
#define RECOVERED_LOCOMOTION_ACTION_SERVICE_10 10U

static float recovered_locomotion_action_float(u32 bits)
{
    union {
        u32 bits;
        float value;
    } input;

    input.bits = bits;
    return input.value;
}

static u32 recovered_locomotion_action_bits(float value)
{
    union {
        u32 bits;
        float value;
    } output;

    output.value = value;
    return output.bits;
}

/* 0x27558/0x3290c: the config pointer lives at object+0x6c. */
static volatile unsigned char *recovered_locomotion_action_config(
    volatile unsigned char *object)
{
    return (volatile unsigned char *)(unsigned long)
        *(volatile u32 *)(object + 0x6c);
}

/*
 * 0x32f48-0x32f68 and 0x32f90-0x32fb0: the i960 real-long multiply.  `movr
 * g4,fp0` promotes the single to double, `mov 0,g4` / `lda <high word>,g5`
 * form the double multiplier in the g4:g5 pair, `mulrl fp0,g4,g4` multiplies
 * and `movrl g4,fp0` / `movr fp0,g4` round the double product back to a
 * single for the +0x1c4 store.
 */
static void recovered_locomotion_action_rescale(
    volatile unsigned char *object, double factor)
{
    float value = recovered_locomotion_action_float(
        *(volatile u32 *)(object + 0x1c4));

    *(volatile u32 *)(object + 0x1c4) =
        recovered_locomotion_action_bits((float)((double)value * factor));
}

/*
 * Pure body of arm 0 (0x329c4-0x32a88).  `state_table` is the 0x32564 word1
 * base of the 16-byte-stride state table and `mode_target` is g3+0x1a; the
 * _run wrapper supplies the original absolute addresses.
 */
void recovered_locomotion_action_0_core(
    volatile unsigned char *object,
    const volatile unsigned char *state_table,
    volatile unsigned short *mode_target)
{
    volatile unsigned char *cfg = recovered_locomotion_action_config(object);
    s32 state = (s32)(s16)*(volatile u16 *)(object + 0x172);
    u32 gate = *(const volatile u32 *)(state_table + (state * 16));

    /* 0x329d8: flag == 0 skips the whole +0x2e auto-face block. */
    if (gate != 0U) {
        u32 facing = (u32)*(volatile u16 *)(object + 0x184);
        u32 bias = (u32)*(volatile u16 *)(object + 0x34);
        u32 current = (u32)*(volatile u16 *)(object + 0x2e);
        u32 raw = (facing + bias) - current;
        s32 delta = (s16)(u16)raw;
        s32 step;

        if (delta > (s32)RECOVERED_LOCOMOTION_ACTION_SLEW_LIMIT)
            step = (s32)RECOVERED_LOCOMOTION_ACTION_SLEW_LIMIT;
        else if (delta < -(s32)RECOVERED_LOCOMOTION_ACTION_SLEW_LIMIT)
            step = -(s32)RECOVERED_LOCOMOTION_ACTION_SLEW_LIMIT;
        else
            step = (s32)raw;

        /* 0x32a20-0x32a28: +0x2e += clamped delta. */
        *(volatile u16 *)(object + 0x2e) = (u16)(current + (u32)step);

        /* 0x32a2c-0x32a48: +0x184 += +0x10a and +0x2e += +0x10a. */
        *(volatile u16 *)(object + 0x184) = (u16)(
            (u32)*(volatile u16 *)(object + 0x184)
            + (u32)*(volatile u16 *)(object + 0x10a));
        *(volatile u16 *)(object + 0x2e) = (u16)(
            (u32)*(volatile u16 *)(object + 0x2e)
            + (u32)*(volatile u16 *)(object + 0x10a));
    }

    /* 0x32a4c-0x32cf4: carry +0x184 into the g3+0x1a mode target, clamped by
     * +/-cfg+0x528.  The unsaturated arm adds the raw 32-bit difference, so
     * the target lands exactly on +0x184. */
    {
        u32 limit = *(volatile u32 *)(
            cfg + RECOVERED_LOCOMOTION_ACTION_TURN_LIMIT);
        u32 raw = (u32)*(volatile u16 *)(object + 0x184)
                - (u32)*mode_target;
        s32 delta = (s16)(u16)raw;
        s32 step;

        if (delta > (s32)limit)
            step = (s32)limit;
        else if (delta < -(s32)limit)
            step = -(s32)limit;
        else
            step = (s32)raw;

        *mode_target = (u16)((u32)*mode_target + (u32)step);
    }
}

/* Original ABI wrapper: absolute 0x32564 state table and the 0x504be0/
 * 0x504b90 g3 mode table selected by object+0x30. */
void recovered_locomotion_action_0_run(volatile unsigned char *object)
{
    const volatile unsigned char *state_table =
        (const volatile unsigned char *)(unsigned long)
        RECOVERED_LOCOMOTION_ACTION_STATE_TABLE;
    volatile unsigned short *mode_target =
        (volatile unsigned short *)(unsigned long)
        (((u32)*(volatile u16 *)(object + 0x30) != 0U)
            ? (RECOVERED_LOCOMOTION_ACTION_MODE_TABLE_NONZERO
               + RECOVERED_LOCOMOTION_ACTION_MODE_TARGET_OFFSET)
            : (RECOVERED_LOCOMOTION_ACTION_MODE_TABLE_ZERO
               + RECOVERED_LOCOMOTION_ACTION_MODE_TARGET_OFFSET));

    recovered_locomotion_action_0_core(object, state_table, mode_target);
}

/*
 * Pure body of arm 12 (0x32ea4-0x32fd0).  The opcode-10 projection response
 * is the cached low half at object+0x84 written by the 0x32810 prefix; the
 * live 0x884000 exchange is the external equivalent.
 */
void recovered_locomotion_action_12_core(volatile unsigned char *object)
{
    volatile unsigned char *cfg = recovered_locomotion_action_config(object);
    u32 response = (u32)*(volatile u16 *)(object + 0x84);
    u32 current = (u32)*(volatile u16 *)(object + 0x2e);
    u32 raw = response - current;
    s32 delta = (s16)(u16)raw;
    u32 limit = *(volatile u32 *)(
        cfg + RECOVERED_LOCOMOTION_ACTION_SNAP_LIMIT);

    /* 0x32efc-0x32f14: delta above +cfg+0x52c saturates high. */
    if ((s32)limit < delta) {
        *(volatile u16 *)(object + 0x2e) = (u16)(current + limit);
        if ((u32)*(volatile u16 *)(object + 0x19c) != 0U)
            recovered_locomotion_action_rescale(object, 0.5);
        *(volatile u16 *)(object + 0x184) =
            *(volatile u16 *)(object + 0x2e);
        return;
    }

    /* 0x32f24-0x32f38: delta below -cfg+0x52c saturates low. */
    if (delta < -(s32)limit) {
        *(volatile u16 *)(object + 0x2e) = (u16)(current - limit);
        if ((u32)*(volatile u16 *)(object + 0x19c) != 0U)
            recovered_locomotion_action_rescale(object, 0.5);
        *(volatile u16 *)(object + 0x184) =
            *(volatile u16 *)(object + 0x2e);
        return;
    }

    /* 0x32f70-0x32fb0: the (response + 0x400) & 0xffff > 0x800 quadrant test
     * with +0x19c set rescales the speed by 0.75. */
    if ((((response + 0x400U) & 0xffffU) > 0x800U)
        && ((u32)*(volatile u16 *)(object + 0x19c) != 0U))
        recovered_locomotion_action_rescale(object, 0.75);

    /* 0x32fb4-0x32fc8: +0x2e += raw delta, clear +0x1b2, then +0x184 = +0x2e. */
    *(volatile u16 *)(object + 0x2e) = (u16)(current + raw);
    *(volatile u16 *)(object + 0x1b2) = 0U;
    *(volatile u16 *)(object + 0x184) = *(volatile u16 *)(object + 0x2e);
}

/*
 * Original ABI wrapper for arm 12.  The live body emits the opcode-10 packet
 * from object+0xa4/+0xa8 against object+0x8/+0x10 and reads the response back
 * from 0x884000; the cached +0x84 halfword is the bounded stand-in.
 */
void recovered_locomotion_action_12_run(volatile unsigned char *object)
{
    recovered_locomotion_action_12_core(object);
}
