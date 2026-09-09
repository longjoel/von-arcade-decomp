/* Secondary state seed gate recovered from i960 0x87de4-0x87e10. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_secondary_state_seed_gate_87de4 {
    u32 timing_address;
    u32 timing_value;
    u32 timing_compare_address;
    u32 timing_compare_value;
    u32 state_address;
    u32 state_value;
    u32 seed_value;
    u32 timing_equal;
    u32 state_is_minus_one;
    u32 seed_stored;
    u32 continuation;
};

struct recovered_stage_secondary_state_seed_gate_87de4
recovered_stage_secondary_state_seed_gate_87de4(u32 timing_value,
                                                u32 timing_compare_value,
                                                u32 state_value,
                                                u32 seed_value)
{
    struct recovered_stage_secondary_state_seed_gate_87de4 out;

    out.timing_address = 0x0051d5e4U;
    out.timing_value = timing_value;
    out.timing_compare_address = 0x0051d5e8U;
    out.timing_compare_value = timing_compare_value;
    out.state_address = 0x0051c988U;
    out.state_value = state_value;
    out.seed_value = seed_value;
    out.timing_equal = timing_value == timing_compare_value ? 1U : 0U;
    out.state_is_minus_one = state_value == UINT32_MAX ? 1U : 0U;
    out.seed_stored = out.timing_equal != 0U && out.state_is_minus_one != 0U ? 1U : 0U;
    out.continuation = 0x00087e10U;
    return out;
}
