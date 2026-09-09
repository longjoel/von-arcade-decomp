/* Selector-6 counter follow-up recovered from i960 0x7fd90-0x7fdd4. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_selector6_counter_followup_7fd90_plan {
    u32 control_504e48;
    u32 related_state;
    u32 object_state;
    u32 control_zero_gate_passed;
    u32 related_state7_gate_passed;
    u32 object_state8_gate_passed;
    u32 status_destination;
    u32 published_status;
    u32 state_destination;
    u32 published_state;
    u32 target;
    u32 return_to_selector6_target;
    u32 publication_target;
};

void recovered_transition_selector6_counter_followup_7fd90(
    u32 control_504e48, u32 related_state, u32 object_state,
    struct recovered_transition_selector6_counter_followup_7fd90_plan *plan)
{
    const u32 control_zero = control_504e48 == 0U;
    const u32 related7 = related_state == 7U;
    const u32 object8 = object_state == 8U;
    const u32 return_to_selector6 = control_zero || related7;
    const u32 published = !return_to_selector6;

    plan->control_504e48 = control_504e48;
    plan->related_state = related_state;
    plan->object_state = object_state;
    plan->control_zero_gate_passed = control_zero;
    plan->related_state7_gate_passed = related7;
    plan->object_state8_gate_passed = object8;
    plan->status_destination = published ? 0x00504d94U : 0U;
    plan->published_status = published ? (object8 ? 1U : 22U) : 0U;
    plan->state_destination = published && object8 ? 0x00504d98U : 0U;
    plan->published_state = published && object8 ? 1U : 0U;
    plan->target = return_to_selector6 ? 0x0007fdd4U : 0x0007ff28U;
    plan->return_to_selector6_target = 0x0007fdd4U;
    plan->publication_target = 0x0007ff28U;
}
