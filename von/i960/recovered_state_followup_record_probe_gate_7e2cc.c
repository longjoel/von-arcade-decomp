/* Record-probe gate recovered from i960 0x7e2cc-0x7e33c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_followup_record_probe_gate_7e2cc_plan {
    u32 global_5770f0;
    u32 saved_control;
    u32 saved_selector;
    u32 saved_action;
    u32 published_action;
    u32 record_slot;
    u32 record_halfword_above_threshold;
    u32 global_gate_passed;
    u32 selector_excluded;
    u32 callback_succeeded;
    u32 callback_g1;
    u32 callback_g2;
    u32 enters_success_route;
    u32 continues_to_7e33c;
    u32 callback_target;
    u32 selector_destination;
    u32 selector_value;
    u32 control_destination;
    u32 control_value;
};

void recovered_state_followup_record_probe_gate_7e2cc(
    u32 global_5770f0, u32 selector_g6, u32 record_slot,
    u32 record_halfword_above_threshold, u32 saved_control,
    u32 saved_selector, u32 saved_action, u32 callback_result,
    struct recovered_state_followup_record_probe_gate_7e2cc_plan *plan)
{
    /* 0x7e294-0x7e2d4: establish the probe publication state. */
    const u32 global_passed = global_5770f0 > 9U;
    const u32 excluded = selector_g6 == 0xafU || selector_g6 == 0xa9U;
    const u32 record_passed = record_halfword_above_threshold != 0U;
    const u32 succeeded = callback_result == 1U;
    const u32 enters = global_passed && record_passed && !excluded && succeeded;

    plan->global_5770f0 = global_5770f0;
    plan->saved_control = saved_control;
    plan->saved_selector = saved_selector;
    plan->saved_action = saved_action;
    plan->published_action = 0xffffffffU;
    plan->record_slot = record_slot;
    plan->record_halfword_above_threshold = record_passed;
    plan->global_gate_passed = global_passed;
    plan->selector_excluded = excluded;
    plan->callback_succeeded = succeeded;
    plan->callback_g1 = selector_g6;
    plan->callback_g2 = record_slot;
    plan->enters_success_route = enters;
    plan->continues_to_7e33c = enters ? 0U : 1U;
    plan->callback_target = 0x000816d0U;
    plan->selector_destination = 0U;
    plan->selector_value = 0U;
    plan->control_destination = 0U;
    plan->control_value = 0U;

    if (enters) {
        plan->selector_destination = 0x00504da0U;
        plan->selector_value = selector_g6;
        plan->control_destination = 0x00504d9cU;
        plan->control_value = 1U;
    }
}
