/* Video-transfer workspace prefix recovered from i960 0x1c2c0-0x1c3dc. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_video_transfer_prefix_1c2c0 {
    u32 saved_argument_quadword;
    u32 saved_context_quadword;
    u32 stack_frame_bytes;
    u32 saved_g13;
    u32 saved_g14;
    u32 fp_register_count;
    u32 workspace_base;
    u32 workspace_halfword_count;
    u32 metadata_base;
};

void recovered_video_transfer_prefix_1c2c0(
    struct recovered_video_transfer_prefix_1c2c0 *out)
{
    out->saved_argument_quadword = 1U;
    out->saved_context_quadword = 1U;
    out->stack_frame_bytes = 0x50U;
    out->saved_g13 = 1U;
    out->saved_g14 = 1U;
    out->fp_register_count = 4U;
    out->workspace_base = 0x01008000U;
    out->workspace_halfword_count = 512U;
    out->metadata_base = 0x0100a000U;
}

/* Pure form of the nonzero 0x504d34 branch. The original loop adds the
 * signed halfword base at 0x504d24 to each source halfword. */
u32 recovered_video_transfer_rebase_1c2c0(
    const int16_t *source, int16_t base, int16_t *destination,
    u32 capacity)
{
    u32 index;
    u32 count = capacity < 512U ? capacity : 512U;

    for (index = 0U; index < count; ++index)
        destination[index] = (int16_t)(source[index] + base);
    return count;
}
