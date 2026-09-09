/* Secondary fallback recovered from i960 0x814b4-0x81528. */
#include <stdint.h>

typedef uint32_t u32;

static float float_from_bits(u32 bits)
{
    union {
        u32 bits;
        float value;
    } converted = {bits};
    return converted.value;
}

struct recovered_transition_secondary_fallback_814b4_plan {
    u32 control_504dc8;
    u32 current_state_504d68;
    u32 result_table;
    u32 result_value;
    u32 result_destination;
    u32 control_one;
    float timing_504d60;
    float timing_threshold;
    u32 timing_float_passed;
    u32 status_destination;
    u32 initial_status;
    u32 final_status;
    u32 state_destination;
    u32 published_state;
    u32 control_failure_target;
    u32 timing_pass_target;
    u32 timing_fail_target;
    u32 target;
};

void recovered_transition_secondary_fallback_814b4(
    u32 control_504dc8,
    u32 current_state_504d68,
    u32 result_value,
    float timing_504d60,
    struct recovered_transition_secondary_fallback_814b4_plan *plan)
{
    const u32 control_one = control_504dc8 == 1U ? 1U : 0U;
    const float timing_threshold = float_from_bits(0x40690000U);
    const u32 timing_passed = timing_504d60 < timing_threshold ? 1U : 0U;

    plan->control_504dc8 = control_504dc8;
    plan->current_state_504d68 = current_state_504d68;
    plan->result_table = 0x000728a0U;
    plan->result_value = result_value;
    plan->result_destination = 0x00504d94U;
    plan->control_one = control_one;
    plan->timing_504d60 = timing_504d60;
    plan->timing_threshold = timing_threshold;
    plan->timing_float_passed = timing_passed;
    plan->status_destination = control_one != 0U ? 0x00504d94U : 0U;
    plan->initial_status = control_one != 0U ? 23U : 0U;
    plan->final_status = control_one != 0U ?
        timing_passed != 0U ? 23U : 8U : 0U;
    plan->state_destination = control_one != 0U && timing_passed != 0U
        ? 0x00504d98U : 0U;
    plan->published_state = control_one != 0U && timing_passed != 0U ? 1U : 0U;
    plan->control_failure_target = 0x000815e0U;
    plan->timing_pass_target = 0x000815e0U;
    plan->timing_fail_target = 0x000815e0U;
    plan->target = plan->control_failure_target;
}
