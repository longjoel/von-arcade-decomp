/* State-31 selector/publication arm recovered from 0x7ed34-0x7edc0. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state31_selector_publication_7ed34_plan {
    u32 status_gate_passed;
    u32 state_mode_gate_passed;
    u32 selector_gate_passed;
    u32 enters_route;
    u32 state2_publication;
    u32 continuation_target;
    u32 status_destination;
    u32 status_value;
    u32 selector_destination;
    u32 selector_value;
    u32 control_destination;
    u32 control_value;
    u32 action_destination;
    u32 action_value;
    u32 continuation_destination;
    u32 continuation_value;
};

void recovered_state31_selector_publication_7ed34(
    u32 status_504d68, u32 related_state_64, u32 mode_504e30,
    u32 selector_504e4c, u32 caller_continuation,
    struct recovered_state31_selector_publication_7ed34_plan *plan)
{
    const u32 status_passed = status_504d68 == 0U || status_504d68 == 9U;
    const u32 state_mode_passed =
        (related_state_64 == 3U && (mode_504e30 & (1U << 2)) != 0U) ||
        (related_state_64 == 2U && (mode_504e30 & (1U << 1)) != 0U);
    const u32 selector_passed = selector_504e4c == 0U;
    const u32 enters = status_passed && state_mode_passed && selector_passed;
    const u32 state2 = enters && related_state_64 == 2U;

    plan->status_gate_passed = status_passed;
    plan->state_mode_gate_passed = state_mode_passed;
    plan->selector_gate_passed = selector_passed;
    plan->enters_route = enters;
    plan->state2_publication = state2;
    plan->continuation_target = !enters ? 0x0007ee28U :
                                 (state2 ? 0U : 0x0007edc4U);
    plan->status_destination = state2 ? 0x00504d94U : 0U;
    plan->status_value = state2 ? caller_continuation : 0U;
    plan->selector_destination = state2 ? 0x00504d98U : 0U;
    plan->selector_value = state2 ? 2U : 0U;
    plan->control_destination = state2 ? 0x00504d9cU : 0U;
    plan->control_value = state2 ? 3U : 0U;
    plan->action_destination = state2 ? 0x00504db8U : 0U;
    plan->action_value = state2 ? 25U : 0U;
    plan->continuation_destination = state2 ? 0x00504da0U : 0U;
    plan->continuation_value = state2 ? 0x64U : 0U;
}
