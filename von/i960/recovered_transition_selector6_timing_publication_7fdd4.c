/* Selector-6 timing publication gate recovered from i960 0x7fdd4-0x7fe24. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_selector6_timing_publication_7fdd4_plan {
    u32 object_state;
    u32 related_state;
    u32 related_17a_shifted;
    u32 object_state_gate_passed;
    u32 related_state_gate_passed;
    u32 timing_gate_passed;
    u32 publication_gate_passed;
    u32 state_destination;
    u32 state_value;
    u32 action_destination;
    u32 action_value;
    u32 target;
    u32 alternate_target;
};

void recovered_transition_selector6_timing_publication_7fdd4(
    u32 object_state, u32 related_state, u32 related_17a_shifted,
    struct recovered_transition_selector6_timing_publication_7fdd4_plan *plan)
{
    const u32 object_passed = object_state == 0U || object_state == 6U;
    const u32 related_passed = related_state == 0U || related_state == 6U;
    const u32 timing_passed = related_17a_shifted <= 0x90000U;
    const u32 published = object_passed && related_passed && timing_passed;

    plan->object_state = object_state;
    plan->related_state = related_state;
    plan->related_17a_shifted = related_17a_shifted;
    plan->object_state_gate_passed = object_passed;
    plan->related_state_gate_passed = related_passed;
    plan->timing_gate_passed = timing_passed;
    plan->publication_gate_passed = published;
    plan->state_destination = published ? 0x00504d98U : 0U;
    plan->state_value = published ? 6U : 0U;
    plan->action_destination = published ? 0x00504db8U : 0U;
    plan->action_value = published ? 20U : 0U;
    plan->target = published ? 0x0007fe20U : 0x0007fe24U;
    plan->alternate_target = 0x0007fe24U;
}
