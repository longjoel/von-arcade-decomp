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
    u32 candidate_index, uint8_t map_byte, uint16_t previous_word,
    uint16_t current_word, uint8_t object_byte)
{
    struct recovered_scheduler_callback_secondary_gate_85f8c out;

    out.candidate_index = candidate_index;
    out.route = RECOVERED_SECONDARY_REJECT;
    out.map_bit6 = 0U;
    out.previous_special_bits = 0U;
    out.current_is_zero = 0U;
    out.object_byte_is_zero = 0U;

    out.map_bit6 = (map_byte & (1U << 6)) != 0U;
    out.previous_special_bits = (previous_word &
        ((1U << 9) | (1U << 8) | (1U << 11))) != 0U;
    out.current_is_zero = current_word == 0U;
    out.object_byte_is_zero = object_byte == 0U;
    if (!out.map_bit6)
        return out;
    out.route = (out.previous_special_bits || out.current_is_zero ||
        out.object_byte_is_zero) ? RECOVERED_SECONDARY_PRIMARY_86000 :
        RECOVERED_SECONDARY_FALLBACK_860a0;
    return out;
}
