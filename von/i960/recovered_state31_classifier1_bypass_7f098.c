/* Classifier-1 bypass route recovered from i960 0x7f098-0x7f0d0. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state31_classifier1_bypass_7f098_plan {
    u32 object_state;
    u32 related_state;
    u32 selector;
    u32 object_state_passed;
    u32 related_state_passed;
    u32 selector_passed;
    u32 gate_passed;
    u32 target;
    u32 published_status;
    u32 callback_target;
    u32 callback_argument;
    u32 action_destination;
    u32 action_value;
    u32 control_destination;
    u32 control_value;
    u32 selector_destination;
    u32 selector_value;
    u32 failure_target;
};

void recovered_state31_classifier1_bypass_7f098(
    u32 object_state, u32 related_state, u32 selector, u32 related_pointer,
    struct recovered_state31_classifier1_bypass_7f098_plan *plan)
{
    const u32 object_passed = object_state == 6U ? 1U : 0U;
    const u32 related_passed = related_state == 3U ? 1U : 0U;
    const u32 selector_passed = selector == 0U || selector == 2U || selector == 5U;
    const u32 gate_passed = object_passed && related_passed && selector_passed;

    plan->object_state = object_state;
    plan->related_state = related_state;
    plan->selector = selector;
    plan->object_state_passed = object_passed;
    plan->related_state_passed = related_passed;
    plan->selector_passed = selector_passed ? 1U : 0U;
    plan->gate_passed = gate_passed;
    plan->target = gate_passed ? 0x0007f0bcU : 0x0007f0f8U;
    plan->published_status = gate_passed ? 7U : 0U;
    plan->callback_target = gate_passed ? 0x00079d60U : 0U;
    plan->callback_argument = gate_passed ? related_pointer : 0U;
    plan->action_destination = gate_passed ? 0x00504db8U : 0U;
    plan->action_value = gate_passed ? 30U : 0U;
    plan->control_destination = gate_passed ? 0x00504da0U : 0U;
    plan->control_value = gate_passed ? 3U : 0U;
    plan->selector_destination = gate_passed ? 0x00504d9cU : 0U;
    plan->selector_value = gate_passed ? 0x64U : 0U;
    plan->failure_target = 0x0007f0f8U;
}
