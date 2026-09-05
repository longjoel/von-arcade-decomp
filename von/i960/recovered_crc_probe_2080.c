/* Adjusted CRC probe recovered from i960 0x2080-0x2090. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_crc_probe_plan {
    u32 checksum_helper;
    u32 pointer_adjust;
    u32 byte_count;
    u32 byte_stride;
    u32 checksum_mask;
    u32 data_address;
};

void recovered_crc_probe_plan(u32 base, struct recovered_crc_probe_plan *plan)
{
    plan->checksum_helper = 0x00003120U;
    plan->pointer_adjust = 12U;
    /* addo 31,7,g2: the count is the literal sum, matching the 0x22f0
     * writer's addo 31,3,g2 idiom with a wider 38-byte window. */
    plan->byte_count = 38U;
    plan->byte_stride = 1U;
    /* Callers reload the stored slot with ldos and mask both sides with
     * 0xffff before comparing, so only the low 16 bits are significant. */
    plan->checksum_mask = 0xffffU;
    plan->data_address = base + 12U;
}
