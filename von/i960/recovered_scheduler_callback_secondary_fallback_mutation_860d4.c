/* Secondary-map fallback mutation recovered from i960 0x860d4-0x86174. */

#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_scheduler_callback_secondary_fallback_mutation_860d4 {
    u32 candidate_index;
    u32 candidate_nibble;
    u32 row_offset;
    s32 current_before;
    s32 current_after;
    s32 paired_before;
    s32 paired_after;
    u32 map_replaced;
    uint8_t map_after[32];
};

struct recovered_scheduler_callback_secondary_fallback_mutation_860d4
recovered_scheduler_callback_secondary_fallback_mutation_860d4(
    const uint8_t map_before[32], u32 candidate_index, uint8_t callback_g14,
    u32 state, u32 selector, s32 current_value, s32 paired_value)
{
    struct recovered_scheduler_callback_secondary_fallback_mutation_860d4 out;
    u32 index;

    out.candidate_index = candidate_index;
    out.candidate_nibble = map_before[candidate_index] & 0x0fU;
    out.row_offset = state * 1088U + selector * 136U + 0x86U;
    out.current_before = current_value;
    out.current_after = current_value - 10;
    out.paired_before = paired_value;
    out.paired_after = paired_value;
    out.map_replaced = 0U;
    for (index = 0U; index < 32U; ++index)
        out.map_after[index] = map_before[index];

    if (paired_value <= 49)
        out.paired_after = 40;
    out.map_after[candidate_index] = callback_g14;
    out.map_replaced = 1U;
    return out;
}
