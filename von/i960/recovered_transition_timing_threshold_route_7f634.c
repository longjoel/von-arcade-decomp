/* Timing threshold route recovered from i960 0x7f634-0x7f6b0. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_timing_threshold_route_7f634_plan {
    u32 lower_threshold_above_current;
    u32 current_below_upper_threshold;
    u32 global_504da4;
    u32 global_504dc8;
    u32 lower_arm_taken;
    u32 upper_arm_taken;
    u32 upper_globals_passed;
    u32 callback_target;
    u32 selector_destination;
    u32 selector_value;
    u32 control_destination;
    u32 control_value;
    u32 state_destination;
    u32 state_value;
    u32 route_mode;
    u32 target;
    u32 failure_target;
};

void recovered_transition_timing_threshold_route_7f634(
    u32 lower_threshold_above_current, u32 current_below_upper_threshold,
    u32 global_504da4, u32 global_504dc8,
    struct recovered_transition_timing_threshold_route_7f634_plan *plan)
{
    const u32 lower_arm = lower_threshold_above_current ? 1U : 0U;
    const u32 upper_arm = !lower_arm;
    const u32 globals_passed = global_504da4 == 1U && global_504dc8 == 1U;
    const u32 upper_route = upper_arm && current_below_upper_threshold &&
                            globals_passed;

    plan->lower_threshold_above_current = lower_arm;
    plan->current_below_upper_threshold = current_below_upper_threshold ? 1U : 0U;
    plan->global_504da4 = global_504da4;
    plan->global_504dc8 = global_504dc8;
    plan->lower_arm_taken = lower_arm;
    plan->upper_arm_taken = upper_arm;
    plan->upper_globals_passed = globals_passed ? 1U : 0U;
    plan->callback_target = lower_arm ? 0x00082800U : 0U;
    plan->selector_destination = lower_arm ? 0x00504d9cU : 0U;
    plan->selector_value = lower_arm ? 4U : 0U;
    plan->control_destination = lower_arm ? 0x00504da0U : 0U;
    plan->control_value = lower_arm ? 0x64U : 0U;
    plan->state_destination = upper_route ? 0x00504d98U : 0U;
    plan->state_value = upper_route ? 1U : 0U;
    plan->route_mode = upper_route ? 10U : 0U;
    plan->target = lower_arm ? 0x0007f66cU :
                   (upper_route ? 0x0007f8fcU : 0x0007f6b0U);
    plan->failure_target = 0x0007f6b0U;
}
