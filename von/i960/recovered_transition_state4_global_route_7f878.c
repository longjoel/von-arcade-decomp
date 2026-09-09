/* State-4 global route recovered from i960 0x7f878-0x7f918. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_state4_global_route_7f878_plan {
    u32 global_504d70;
    int32_t related_184;
    int32_t current_184;
    int32_t difference_input;
    u32 direct_table_value;
    u32 classifier_result;
    u32 global_negative_arm;
    u32 global_direct_arm;
    u32 global_positive_arm;
    u32 result_from_table;
    u32 status_destination;
    u32 published_status;
    u32 callback_target;
    u32 callback_argument;
    u32 action_destination;
    u32 action_value;
    u32 control_destination;
    u32 control_value;
    u32 selector_destination;
    u32 selector_value;
    u32 target;
};

void recovered_transition_state4_global_route_7f878(
    u32 global_504d70, int32_t related_184, int32_t current_184,
    int32_t classifier_result, u32 direct_table_value, u32 control_value,
    u32 related_pointer,
    struct recovered_transition_state4_global_route_7f878_plan *plan)
{
    const u32 negative = global_504d70 <= 1U;
    const u32 direct = global_504d70 >= 2U && global_504d70 <= 7U;
    const u32 positive = global_504d70 > 7U;
    const int32_t bias = negative ? -0x5000 : 0x5000;

    plan->global_504d70 = global_504d70;
    plan->related_184 = related_184;
    plan->current_184 = current_184;
    plan->difference_input = related_184 - (current_184 + bias);
    plan->direct_table_value = direct_table_value;
    plan->classifier_result = classifier_result;
    plan->global_negative_arm = negative;
    plan->global_direct_arm = direct;
    plan->global_positive_arm = positive;
    plan->result_from_table = direct ? direct_table_value : (u32)classifier_result;
    plan->status_destination = 0x00504d94U;
    plan->published_status = plan->result_from_table;
    plan->callback_target = 0x00079050U;
    plan->callback_argument = related_pointer;
    plan->action_destination = 0x00504db8U;
    plan->action_value = 30U;
    plan->control_destination = 0x00504da0U;
    plan->control_value = control_value;
    plan->selector_destination = 0x00504d9cU;
    plan->selector_value = 4U;
    plan->target = 0x0007f918U;
}
