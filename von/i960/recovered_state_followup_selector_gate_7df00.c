/* Selector gate recovered from i960 0x7df00-0x7df58. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_followup_selector_gate_7df00_plan {
    u32 enters_status7_route;
    u32 continues_to_7df58;
    u32 status_destination;
    u32 status_value;
    u32 control_destination;
    u32 control_value;
    u32 selector_destination;
    u32 selector_value;
    u32 call_target;
};

void recovered_state_followup_selector_gate_7df00(
    u32 selector_r6, u32 object_field_64,
    struct recovered_state_followup_selector_gate_7df00_plan *plan)
{
    (void)object_field_64;
    plan->enters_status7_route = selector_r6 == 0x44U ? 0U : 1U;
    plan->continues_to_7df58 = selector_r6 == 0x44U ? 1U : 0U;
    plan->status_destination = 0U;
    plan->status_value = 0U;
    plan->control_destination = 0U;
    plan->control_value = 0U;
    plan->selector_destination = 0U;
    plan->selector_value = 0U;
    plan->call_target = 0U;

    if (plan->enters_status7_route != 0U) {
        plan->status_destination = 0x00504d94U;
        plan->status_value = 7U;
        plan->control_destination = 0x00504d9cU;
        plan->control_value = 1U;
        plan->selector_destination = 0x00504da0U;
        plan->selector_value = selector_r6;
        plan->call_target = 0x00079d60U;
    }
}
