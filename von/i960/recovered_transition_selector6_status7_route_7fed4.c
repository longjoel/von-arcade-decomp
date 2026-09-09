/* Selector-6/status-7 route recovered from i960 0x7fed4-0x7ff34. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_selector6_status7_route_7fed4_plan {
    u32 related_172;
    u32 global_counter;
    u32 callback_argument;
    u32 related_172_gate_passed;
    u32 counter_gate_passed;
    u32 admission_passed;
    u32 selector_destination;
    u32 selector_value;
    u32 control_destination;
    u32 control_value;
    u32 counter_destination;
    int32_t counter_value;
    u32 status_destination;
    u32 status_value;
    u32 callback_target;
    u32 action_destination;
    u32 action_value;
    u32 target;
    u32 failure_target;
};

void recovered_transition_selector6_status7_route_7fed4(
    u32 related_172, u32 global_counter, u32 callback_argument,
    struct recovered_transition_selector6_status7_route_7fed4_plan *plan)
{
    const u32 halfword_passed = related_172 == 27U || related_172 == 30U;
    const u32 counter_passed = global_counter > 0x5dcU;
    const u32 admitted = halfword_passed && counter_passed;

    plan->related_172 = related_172;
    plan->global_counter = global_counter;
    plan->callback_argument = callback_argument;
    plan->related_172_gate_passed = halfword_passed;
    plan->counter_gate_passed = counter_passed;
    plan->admission_passed = admitted;
    plan->selector_destination = admitted ? 0x00504d9cU : 0U;
    plan->selector_value = admitted ? 6U : 0U;
    plan->control_destination = admitted ? 0x00504da0U : 0U;
    plan->control_value = admitted ? 0x64U : 0U;
    plan->counter_destination = admitted ? 0x00504db4U : 0U;
    plan->counter_value = admitted ? -1 : 0;
    plan->status_destination = admitted ? 0x00504d94U : 0U;
    plan->status_value = admitted ? 7U : 0U;
    plan->callback_target = admitted ? 0x00079d60U : 0U;
    plan->action_destination = admitted ? 0x00504db8U : 0U;
    plan->action_value = admitted ? 30U : 0U;
    plan->target = 0x0007ff34U;
    plan->failure_target = 0x0007ff34U;
}
