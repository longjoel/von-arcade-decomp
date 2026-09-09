/* Secondary stage state/timing prefix recovered from i960 0x87b2c-0x87c2c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_secondary_state_prefix_87b2c {
    u32 state_address;
    u32 state_before;
    u32 state_after;
    u32 timing_address;
    u32 timing_before;
    u32 timing_candidate;
    u32 timing_after;
    u32 timing_limit;
    u32 route_word;
    u32 selected_buffer;
    u32 first_service_target;
    u32 fixed_call_targets[6];
    u32 buffer_service_target;
    u32 final_service_target;
};

struct recovered_stage_secondary_state_prefix_87b2c
recovered_stage_secondary_state_prefix_87b2c(u32 state_value,
                                             u32 timing_value,
                                             u32 route_word)
{
    struct recovered_stage_secondary_state_prefix_87b2c out;
    u32 timing_candidate = timing_value;

    out.state_address = 0x0051c988U;
    out.state_before = state_value;
    out.state_after = state_value;
    out.timing_address = 0x0051d5e4U;
    out.timing_before = timing_value;
    out.timing_limit = 0x77U;
    out.route_word = route_word;
    if (state_value > 0U) {
        timing_candidate = timing_value + 1U;
    } else {
        out.state_after = state_value + 1U;
    }
    out.timing_candidate = timing_candidate;
    out.timing_after = timing_candidate <= out.timing_limit ? timing_candidate : 0U;
    out.selected_buffer = route_word == 0U ? 0x00503ad0U : 0x005040d0U;
    out.first_service_target = 0x00088620U;
    out.fixed_call_targets[0] = 0x000c8f10U;
    out.fixed_call_targets[1] = 0x0006fec0U;
    out.fixed_call_targets[2] = 0x0009b308U;
    out.fixed_call_targets[3] = 0x0006fec0U;
    out.fixed_call_targets[4] = 0x000c8f60U;
    out.fixed_call_targets[5] = 0x00000000U;
    out.buffer_service_target = 0x0009baa0U;
    out.final_service_target = 0x000de990U;
    return out;
}
