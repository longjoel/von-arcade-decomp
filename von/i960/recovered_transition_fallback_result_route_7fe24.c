/* Fallback result route recovered from i960 0x7fe24-0x7fed0. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_fallback_result_route_7fe24_plan {
    u32 global_counter;
    u32 global_504d70;
    int32_t related_184;
    int32_t current_184;
    int32_t difference_input;
    int32_t offset;
    u32 counter_shortcut;
    u32 negative_global_arm;
    u32 positive_global_arm;
    u32 classifier_result;
    u32 direct_table_result;
    u32 result_table;
    u32 selected_result;
    u32 action_destination;
    u32 action_value;
    u32 status_destination;
    u32 published_status;
    u32 callback_gate;
    u32 callback_target;
    u32 callback_argument;
    u32 target;
};

void recovered_transition_fallback_result_route_7fe24(
    u32 global_counter, u32 global_504d70, int32_t related_184,
    int32_t current_184, int32_t classifier_result, u32 direct_table_result,
    u32 callback_gate, u32 related_pointer,
    struct recovered_transition_fallback_result_route_7fe24_plan *plan)
{
    const u32 shortcut = global_counter <= 0x2bcU;
    const u32 negative = !shortcut && global_504d70 < 4U;
    const u32 positive = !shortcut && global_504d70 >= 4U;
    const int32_t offset = negative ? -0x6580 : 0x6580;
    const int32_t difference = related_184 - (current_184 + offset);
    const u32 result = shortcut ? direct_table_result : (u32)classifier_result;

    plan->global_counter = global_counter;
    plan->global_504d70 = global_504d70;
    plan->related_184 = related_184;
    plan->current_184 = current_184;
    plan->difference_input = difference;
    plan->offset = offset;
    plan->counter_shortcut = shortcut;
    plan->negative_global_arm = negative;
    plan->positive_global_arm = positive;
    plan->classifier_result = classifier_result;
    plan->direct_table_result = direct_table_result;
    plan->result_table = shortcut ? 0x00072720U : 0x00072780U;
    plan->selected_result = result;
    plan->action_destination = 0x00504db8U;
    plan->action_value = 30U;
    plan->status_destination = 0x00504d94U;
    plan->published_status = result;
    plan->callback_gate = callback_gate;
    plan->callback_target = callback_gate == 1U ? 0x00079050U : 0U;
    plan->callback_argument = callback_gate == 1U ? related_pointer : 0U;
    plan->target = 0x0007fed0U;
}
