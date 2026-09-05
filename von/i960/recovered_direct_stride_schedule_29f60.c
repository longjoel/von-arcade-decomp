/* Direct-path dispatch and stride schedule for mode-0 uploads.
 *
 * At 0x29f60 the fade value in 0x51a260 selects the direct loop form:
 * cmpible 0,r14 exits to 0x2a00c (fade form, factor = fade) when the
 * value is at most zero, otherwise r13 = fade + 0x100 drives the scale
 * form. Both forms run the same cadence as the blend path (32-texel
 * inner loops, body-first r15 block over 8 passes), but every outer
 * bottom (0x29fe0 and 0x2a094) advances all six pointers by 0x180, so
 * each pair totals 0x80 + 0x180 = 0x200 per pass: exactly one 4KB bank
 * over the run, with no pair-2 asymmetry.
 */
#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_direct_stride_schedule {
    u32 fade_addr;
    s32 use_fade_form;
    u32 factor;
    u32 outer_iterations;
    u32 pass_advance;
    u32 src0_end;
    u32 dst0_end;
    u32 src1_end;
    u32 dst1_end;
    u32 src2_end;
    u32 dst2_end;
};

void recovered_direct_stride_schedule_plan(s32 fade,
                                            u32 src0, u32 dst0,
                                            u32 src1, u32 dst1,
                                            u32 src2, u32 dst2,
                                            struct recovered_direct_stride_schedule *plan)
{
    plan->fade_addr = 0x0051a260U;
    /* cmpible 0,r14,0x2a00c: fade values at most zero take the 0x2a00c
     * fade form; anything above runs the scale form with fade + 0x100. */
    plan->use_fade_form = fade <= 0 ? 1 : 0;
    plan->factor = plan->use_fade_form ? (u32)fade : (u32)fade + 0x100U;
    plan->outer_iterations = 8U;
    plan->pass_advance = 0x80U + 0x180U;
    {
        u32 total = plan->pass_advance * plan->outer_iterations;
        plan->src0_end = src0 + total;
        plan->dst0_end = dst0 + total;
        plan->src1_end = src1 + total;
        plan->dst1_end = dst1 + total;
        plan->src2_end = src2 + total;
        plan->dst2_end = dst2 + total;
    }
}
