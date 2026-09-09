/* Primary secondary-map mutation recovered from i960 0x86000-0x8609c. */

#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_scheduler_callback_secondary_primary_86000 {
    u32 candidate_index;
    u32 candidate_nibble;
    uint8_t candidate_after;
    u32 row_offset;
    s32 current_before;
    s32 current_after;
    s32 paired_before;
    s32 paired_after;
    u32 candidate_replaced;
    u32 collision;
    u32 exits_without_pair_write;
};

struct recovered_scheduler_callback_secondary_primary_86000
recovered_scheduler_callback_secondary_primary_86000(
    const uint8_t map_before[32], u32 candidate_index, uint8_t callback_g14,
    u32 state, u32 selector, s32 current_value, s32 paired_value)
{
    struct recovered_scheduler_callback_secondary_primary_86000 out;
    u32 scan;

    out.candidate_index = candidate_index;
    out.candidate_nibble = map_before[candidate_index] & 0x0fU;
    out.candidate_after = callback_g14;
    out.row_offset = state * 1088U + selector * 136U + 0x86U;
    out.current_before = current_value;
    out.current_after = current_value + 30;
    out.paired_before = paired_value;
    out.paired_after = paired_value;
    out.candidate_replaced = 1U;
    out.collision = 0U;
    out.exits_without_pair_write = 0U;

    for (scan = 0U; scan < 32U; ++scan) {
        uint8_t value = scan == candidate_index ? callback_g14 : map_before[scan];

        if ((value & 0x0fU) == out.candidate_nibble) {
            out.collision = 1U;
            out.exits_without_pair_write = 1U;
            return out;
        }
    }

    /* cmpoble paired_value,1000 branches directly at equality and below. */
    if (paired_value <= 1000) {
        out.exits_without_pair_write = 1U;
    } else {
        out.paired_after = 1000;
    }
    return out;
}
