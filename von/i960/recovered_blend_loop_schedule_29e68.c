/* Blend inner-loop schedule recovered from i960 0x29e68-0x29e94.
 *
 * The plane-1 bit-set loop body runs one masked fade texel per iteration
 * (see recovered_blend_kernel_29dec.c) while the counter/pointer block
 * reduces to a fixed trip schedule: r6 counts 1..32 against the cmpi 31
 * bound, so the body executes 32 times with src/dst advancing 4 bytes
 * per iteration. The b 0x29ec8 exit and the 0x180 stride fixups live
 * outside this inner schedule.
 */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_blend_loop_schedule {
    u32 iterations;
    u32 stores;
    u32 pointer_advance;
    u32 src_end;
    u32 dst_end;
};

void recovered_blend_loop_schedule_plan(u32 src, u32 dst,
                                         struct recovered_blend_loop_schedule *plan)
{
    /* addo r6,1 / cmpi 31,r6 / bge: exits when r6 reaches 32, so the
     * body runs 32 times; each pass advances both pointers by one word. */
    plan->iterations = 32U;
    plan->stores = 32U;
    plan->pointer_advance = 32U * 4U;
    plan->src_end = src + plan->pointer_advance;
    plan->dst_end = dst + plan->pointer_advance;
}
