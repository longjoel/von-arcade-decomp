/* Post-copy stage tail recovered from i960 0x86b98-0x86be0. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_post_copy_tail_86b98 {
    u32 call_count;
    u32 targets[6];
    u32 source_halfword[2];
    u32 destination_halfword[2];
    u32 call_23d60_g0;
    u32 call_71080_g0;
    u32 continuation;
};

struct recovered_stage_post_copy_tail_86b98
recovered_stage_post_copy_tail_86b98(void)
{
    struct recovered_stage_post_copy_tail_86b98 out;

    out.call_count = 6U;
    out.targets[0] = 0x000bece0U;
    out.targets[1] = 0x0009b320U;
    out.targets[2] = 0x00041f20U;
    out.targets[3] = 0x000c5530U;
    out.targets[4] = 0x00023d60U;
    out.targets[5] = 0x00071080U;
    out.source_halfword[0] = 0x0051cbb0U;
    out.source_halfword[1] = 0x0051d1b0U;
    out.destination_halfword[0] = 0x00503ca0U;
    out.destination_halfword[1] = 0x005042a0U;
    out.call_23d60_g0 = 1U;
    out.call_71080_g0 = 0x00503ad0U;
    out.continuation = 0x00086be4U;
    return out;
}
