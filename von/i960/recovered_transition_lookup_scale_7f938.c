/* Lookup and scaling prefix recovered from i960 0x7f938-0x7f9b0. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_lookup_scale_7f938_plan {
    u32 r10;
    u32 r11;
    u32 lookup_byte;
    u32 lookup_index;
    u32 lookup_address;
    u32 raw_value;
    u32 value_nonnegative;
    u32 clamped_value;
    u32 object_state;
    u32 scalar_bits;
    u32 scaled_value;
    u32 lookup_table;
    u32 clamp_bits;
    u32 state2_scalar_bits;
    u32 default_scalar_bits;
    u32 target;
};

void recovered_transition_lookup_scale_7f938(
    u32 r10, u32 r11, u32 lookup_byte, u32 raw_value,
    u32 value_nonnegative, u32 object_state, u32 scaled_value,
    struct recovered_transition_lookup_scale_7f938_plan *plan)
{
    const u32 index = lookup_byte * 3U;
    const u32 nonnegative = value_nonnegative ? 1U : 0U;
    const u32 clamped = nonnegative ? raw_value : 0x42960000U;
    const u32 scalar = object_state == 2U ? 0x40100000U : 0x40080000U;

    plan->r10 = r10;
    plan->r11 = r11;
    plan->lookup_byte = lookup_byte;
    plan->lookup_index = index;
    plan->lookup_address = 0x00562cd8U + index * 16U;
    plan->raw_value = raw_value;
    plan->value_nonnegative = nonnegative;
    plan->clamped_value = clamped;
    plan->object_state = object_state;
    plan->scalar_bits = scalar;
    plan->scaled_value = scaled_value;
    plan->lookup_table = 0x00562cd8U;
    plan->clamp_bits = 0x42960000U;
    plan->state2_scalar_bits = 0x40100000U;
    plan->default_scalar_bits = 0x40080000U;
    plan->target = 0x0007f9b0U;
}
