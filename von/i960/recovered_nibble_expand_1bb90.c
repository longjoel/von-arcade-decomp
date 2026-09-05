/* Nibble-expansion decoder recovered from i960 0x1bb90-0x1bc1c.
 *
 * Each loop pass loads one halfword and reassembles it from scattered
 * bit fields with OR accumulation, storing one expanded halfword:
 * out[4:1] = in[3:0], out[0] = in[12], out[5] = in[13], and the upper
 * field fans out with overlap (out[10] = in[8] | in[14],
 * out[11] = in[9] | in[8], out[12] = in[10] | in[9],
 * out[13] = in[11] | in[10], out[14] = in[11]). All shifted values
 * stay non-negative, so the listing's arithmetic shifts match logical
 * shifts. The run executes max(count, 0) passes (signed entry guard
 * plus body-first counting), advancing src/dst by 2 bytes per pass.
 */
#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;
typedef uint16_t u16;

u16 recovered_nibble_expand_word(u16 pixel)
{
    u32 in = pixel;
    u32 field;
    u32 out;

    out = (in & 15U) << 1;
    field = (in & 0x1000U) >> 12;
    out |= field;
    field = (in & 0x0f00U) << 2;
    out |= field;
    field = (in & 0x2000U) >> 8;
    out |= field;
    field = (in & 0x0f00U) << 3;
    out |= field;
    field = (in & 0x4000U) >> 4;
    out |= field;
    return (u16)out;
}

struct recovered_nibble_expand_run {
    u32 iterations;
    u32 src_end;
    u32 dst_end;
};

void recovered_nibble_expand_run_plan(u32 src, u32 dst, s32 count,
                                       struct recovered_nibble_expand_run *plan)
{
    u32 passes = count > 0 ? (u32)count : 0U;
    plan->iterations = passes;
    plan->src_end = src + passes * 2U;
    plan->dst_end = dst + passes * 2U;
}
