/* State-4 threshold prefix recovered from i960 0x7f70c-0x7f774. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_state4_threshold_prefix_7f70c_plan {
    u32 related_state;
    u32 current_below_407f4000;
    u32 current_below_4072c000;
    u32 outer_state_gate_passed;
    u32 outer_timing_gate_passed;
    u32 selector_destination;
    u32 selector_value;
    u32 control_destination;
    u32 control_value;
    u32 direct_table_arm;
    u32 table_address;
    u32 common_publication_target;
    u32 difference_route_target;
    u32 return_target;
    u32 failure_target;
};

void recovered_transition_state4_threshold_prefix_7f70c(
    u32 related_state, u32 current_below_407f4000,
    u32 current_below_4072c000,
    struct recovered_transition_state4_threshold_prefix_7f70c_plan *plan)
{
    const u32 state_passed = related_state == 4U;
    const u32 outer_passed = current_below_407f4000 ? 1U : 0U;
    const u32 direct = state_passed && outer_passed &&
                       (current_below_4072c000 ? 1U : 0U);

    plan->related_state = related_state;
    plan->current_below_407f4000 = outer_passed;
    plan->current_below_4072c000 = current_below_4072c000 ? 1U : 0U;
    plan->outer_state_gate_passed = state_passed;
    plan->outer_timing_gate_passed = outer_passed;
    plan->selector_destination = state_passed && outer_passed ? 0x00504d9cU : 0U;
    plan->selector_value = state_passed && outer_passed ? 4U : 0U;
    plan->control_destination = state_passed && outer_passed ? 0x00504da0U : 0U;
    plan->control_value = state_passed && outer_passed ? 0x64U : 0U;
    plan->direct_table_arm = direct;
    plan->table_address = direct ? 0x00072780U : 0U;
    plan->common_publication_target = direct ? 0x0007f7d4U : 0U;
    plan->difference_route_target = state_passed && outer_passed ? 0x0007f774U : 0U;
    plan->return_target = state_passed && !outer_passed ? 0x0007f7fcU : 0U;
    plan->failure_target = state_passed ? 0x0007f800U : 0x0007f800U;
}
