/* Recovered i960 0x371e0 frame-step heading/facing integrator (0x37240-0x3734c).
 *
 * This is the part of VON_FN_FRAME_STEP that runs after the input consumer and
 * the byte timers and before the 0x37130 arm dispatch. It is a two-stage
 * proportional slew:
 *
 *   Stage 1 (+0x32, 0x37240-0x372ac):
 *     d1 = (s16)(2*+0x186 - +0x32); slew = clamp(d1, -0x600, 0x600) where an
 *     in-range slew is the full 32-bit 2*+0x186 - +0x32 (so +0x32 snaps to
 *     2*+0x186, otherwise ramps by +-0x600). +0x32 = +0x32 + slew.
 *
 *   Stage 2 (+0x34 and +0x198, 0x37280-0x3734c):
 *     half = 2*+0x186, or (0x8000 + 2*+0x186) & 0xffff when
 *     (u16)(+0x186 + 0xdfff) <= 0x3ffe.  d = half - +0x34.  When
 *     (0x02000000 >= (s32)(d << 16)) or (s16)+0x198 > 0, +0x198 is set to -24
 *     if (s16)d < -0x200 and +0x198 is not negative; otherwise +0x198 = 24.
 *     +0x34 = +0x34 + clamp_s16(d, -0x600, 0x600).
 *
 * Validated bit-exactly against the 25-second original capture normalized to
 * von/tests/fixtures/framestep-heading/original-heading-vectors.json: 541/541
 * +0x32 writes, 541/541 +0x34 writes, 19/19 +0x198 writes.
 */

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed int s32;
typedef signed short s16;

static u16 recovered_framestep_heading_ld16(const volatile unsigned char *object,
                                            u32 offset)
{
    return *(const volatile u16 *)(object + offset);
}

static void recovered_framestep_heading_st16(volatile unsigned char *object,
                                             u32 offset, u32 value)
{
    *(volatile u16 *)(object + offset) = (u16)value;
}

/* 0x37240-0x372ac: +0x32 proportional slew toward 2*+0x186. */
static void recovered_framestep_heading_stage1(volatile unsigned char *object)
{
    u32 a = (u32)recovered_framestep_heading_ld16(object, 0x186U);
    u32 b = (u32)recovered_framestep_heading_ld16(object, 0x32U);
    s32 d = (s32)(2U * a) - (s32)b;
    s32 d16 = (s32)(s16)(u16)d;
    s32 slew;

    if (d16 > 0x600)
        slew = 0x600;
    else if (d16 < -0x600)
        slew = -0x600;
    else
        slew = d;

    recovered_framestep_heading_st16(object, 0x32U,
        (u32)b + (u32)slew);
}

/* 0x37280-0x3734c: +0x34 slew toward the half-heading, with the +0x198
 * descent/air latch. */
static void recovered_framestep_heading_stage2(volatile unsigned char *object)
{
    u32 a = (u32)recovered_framestep_heading_ld16(object, 0x186U);
    u32 c = (u32)recovered_framestep_heading_ld16(object, 0x34U);
    u32 e = (u32)recovered_framestep_heading_ld16(object, 0x198U);
    u32 gate = (a + 0xdfffU) & 0xffffU;
    u32 half = (0x3ffeU < gate) ? ((2U * a) & 0xffffU)
                                : ((0x8000U + 2U * a) & 0xffffU);
    s32 d = (s32)half - (s32)c;
    s32 g7 = d;
    s32 shifted = (s32)((u32)d << 16);

    if ((s32)0x02000000 >= shifted || (s32)(s16)e > 0) {
        if ((s32)(s16)g7 < -0x200 && (e & 0x8000U) == 0U)
            recovered_framestep_heading_st16(object, 0x198U, (u32)-24);
    } else {
        recovered_framestep_heading_st16(object, 0x198U, 24U);
    }

    {
        s32 g4s = (s32)(s16)g7;

        if (g4s > 0x600)
            g7 = 0x600;
        else if (g4s < -0x600)
            g7 = -0x600;
    }

    recovered_framestep_heading_st16(object, 0x34U, (u32)c + (u32)g7);
}

/* Absolute-global entry, inlined into 0x371e0 before the 0x37130 dispatch. */
void recovered_framestep_heading_run(volatile unsigned char *object)
{
    recovered_framestep_heading_stage1(object);
    recovered_framestep_heading_stage2(object);
}
