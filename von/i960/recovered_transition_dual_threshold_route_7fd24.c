/* Dual timing-threshold route recovered from i960 0x7fd24-0x7fd58. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_dual_threshold_route_7fd24_plan {
    u32 object_state;
    u32 first_threshold_above_current;
    u32 second_threshold_above_current;
    u32 first_threshold_gate_passed;
    u32 second_threshold_gate_passed;
    u32 state0_or6_passed;
    u32 state6_second_arm;
    u32 publication_route;
    u32 target;
    u32 publication_target;
    u32 alternate_target;
};

void recovered_transition_dual_threshold_route_7fd24(
    u32 object_state, u32 first_threshold_above_current,
    u32 second_threshold_above_current,
    struct recovered_transition_dual_threshold_route_7fd24_plan *plan)
{
    const u32 first_above = first_threshold_above_current ? 1U : 0U;
    const u32 second_above = second_threshold_above_current ? 1U : 0U;
    const u32 state0_or6 = object_state == 0U || object_state == 6U;
    const u32 state6 = object_state == 6U;
    const u32 publish = (first_above && !state6) ||
                        (second_above && state0_or6);

    plan->object_state = object_state;
    plan->first_threshold_above_current = first_above;
    plan->second_threshold_above_current = second_above;
    plan->first_threshold_gate_passed = first_above;
    plan->second_threshold_gate_passed = second_above;
    plan->state0_or6_passed = state0_or6;
    plan->state6_second_arm = state6 && second_above;
    plan->publication_route = publish;
    plan->target = publish ? 0x0007fd58U : 0x0007fed0U;
    plan->publication_target = 0x0007fd58U;
    plan->alternate_target = 0x0007fed0U;
}
