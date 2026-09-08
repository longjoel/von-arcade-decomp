/* Secondary callback-map routing gate recovered from i960 0x85f8c-0x86000. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_scheduler_callback_secondary_route_85f8c {
    RECOVERED_SECONDARY_REJECT = 0,
    RECOVERED_SECONDARY_PRIMARY_86000 = 1,
    RECOVERED_SECONDARY_FALLBACK_860a0 = 2,
};

struct recovered_scheduler_callback_secondary_gate_85f8c {
    u32 candidate_index;
    u32 route;
    u32 map_bit6;
    u32 previous_special_bits;
    u32 current_is_zero;
    u32 object_byte_is_zero;
};

struct recovered_scheduler_callback_secondary_gate_85f8c
recovered_scheduler_callback_secondary_gate_85f8c(
    const uint8_t map_bytes[32], const uint16_t previous_words[32],
    const uint16_t current_words[32], const uint8_t object_bytes[32])
{
    struct recovered_scheduler_callback_secondary_gate_85f8c out;
    u32 index;

    out.candidate_index = 32U;
    out.route = RECOVERED_SECONDARY_REJECT;
    out.map_bit6 = 0U;
    out.previous_special_bits = 0U;
    out.current_is_zero = 0U;
    out.object_byte_is_zero = 0U;

    for (index = 0U; index < 32U; ++index) {
        u32 map_bit6 = (map_bytes[index] & (1U << 6)) != 0U;
        u32 previous_special = (previous_words[index] &
            ((1U << 9) | (1U << 8) | (1U << 11))) != 0U;
        u32 current_zero = current_words[index] == 0U;
        u32 object_zero = object_bytes[index] == 0U;

        if (!map_bit6)
            continue;
        out.candidate_index = index;
        out.map_bit6 = 1U;
        out.previous_special_bits = previous_special;
        out.current_is_zero = current_zero;
        out.object_byte_is_zero = object_zero;
        out.route = (previous_special || current_zero || object_zero) ?
            RECOVERED_SECONDARY_PRIMARY_86000 :
            RECOVERED_SECONDARY_FALLBACK_860a0;
        return out;
    }
    return out;
}
