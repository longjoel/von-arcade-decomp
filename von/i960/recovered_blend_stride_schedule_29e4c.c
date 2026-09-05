/* Outer-cadence stride schedule for the 0x29d50 blend path.
 *
 * Each outer pass runs three 32-texel inner loops (0x80 bytes per
 * src/dst pointer; see recovered_blend_loop_schedule_29e68.c) joined by
 * 0x180 stride fixups: pair0 (r12/r11) and pair1 (r10/r9) advance once
 * per pass, while pair2 (r8/r7) advances once at the plane transition
 * (0x29ed0/0x29ed8) and again at the outer bottom (0x29f4c/0x29f50).
 * The reloaded mode word selects each plane's loop form once per pass:
 * a set bit takes the fade (add-back) loop, a clear bit the scale loop.
 * The r15 counter block (addo/cmpi 7/bge, body-first) runs 8 passes.
 */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_blend_stride_schedule {
    u32 mode_addr;
    u32 outer_iterations;
    u32 plane_fade[3];
    u32 pass_advance0;
    u32 pass_advance1;
    u32 pass_advance2;
    u32 src0_end;
    u32 dst0_end;
    u32 src1_end;
    u32 dst1_end;
    u32 src2_end;
    u32 dst2_end;
};

#define RECOVERED_BLEND_INNER_ADVANCE 0x80U
#define RECOVERED_BLEND_STRIDE 0x180U

void recovered_blend_stride_schedule_plan(u32 src0, u32 dst0,
                                           u32 src1, u32 dst1,
                                           u32 src2, u32 dst2,
                                           u32 mode,
                                           struct recovered_blend_stride_schedule *plan)
{
    plan->mode_addr = 0x0051a268U;
    plan->outer_iterations = 8U;
    /* chkbit 0/1/2 plus bbc/bno: set bit selects the fade loop. */
    plan->plane_fade[0] = (mode >> 0) & 1U;
    plan->plane_fade[1] = (mode >> 1) & 1U;
    plan->plane_fade[2] = (mode >> 2) & 1U;
    plan->pass_advance0 = RECOVERED_BLEND_INNER_ADVANCE + RECOVERED_BLEND_STRIDE;
    plan->pass_advance1 = RECOVERED_BLEND_INNER_ADVANCE + RECOVERED_BLEND_STRIDE;
    plan->pass_advance2 = RECOVERED_BLEND_INNER_ADVANCE +
        RECOVERED_BLEND_STRIDE + RECOVERED_BLEND_STRIDE;
    plan->src0_end = src0 + plan->pass_advance0 * plan->outer_iterations;
    plan->dst0_end = dst0 + plan->pass_advance0 * plan->outer_iterations;
    plan->src1_end = src1 + plan->pass_advance1 * plan->outer_iterations;
    plan->dst1_end = dst1 + plan->pass_advance1 * plan->outer_iterations;
    plan->src2_end = src2 + plan->pass_advance2 * plan->outer_iterations;
    plan->dst2_end = dst2 + plan->pass_advance2 * plan->outer_iterations;
}
