/* Secondary-map fallback admission recovered from i960 0x860a0-0x860d4. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_callback_secondary_fallback_gate_860a0 {
    u32 map_bit6;
    u32 previous_bit10;
    u32 working_value;
    u32 continues_to_860d4;
    u32 rejects_to_86174;
};

struct recovered_scheduler_callback_secondary_fallback_gate_860a0
recovered_scheduler_callback_secondary_fallback_gate_860a0(
    uint8_t map_byte, uint32_t previous_halfword, uint32_t working_value)
{
    struct recovered_scheduler_callback_secondary_fallback_gate_860a0 out;

    out.map_bit6 = (map_byte & (1U << 6)) != 0U;
    out.previous_bit10 = (previous_halfword & (1U << 10)) != 0U;
    out.working_value = working_value;
    out.continues_to_860d4 = out.map_bit6 &&
        (out.previous_bit10 || working_value != 0U);
    out.rejects_to_86174 = out.continues_to_860d4 ? 0U : 1U;
    return out;
}
