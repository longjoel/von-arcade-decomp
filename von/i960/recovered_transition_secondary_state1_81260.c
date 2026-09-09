/* State-1 secondary body recovered from i960 0x81260-0x812ac. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_secondary_state1_81260_plan {
    u32 related_state_first;
    u32 related_state_second;
    u32 control_504dc8;
    u32 result_table;
    u32 result_value;
    u32 result_destination;
    u32 selector_value;
    u32 first_state6_target;
    u32 state4_target;
    u32 control_failure_target;
    u32 second_state6_target;
    u32 common_target;
    u32 target;
};

/* The second state load is retained because it is a distinct instruction. */
void recovered_transition_secondary_state1_81260(
    u32 related_state_first,
    u32 related_state_second,
    u32 control_504dc8,
    u32 result_value,
    struct recovered_transition_secondary_state1_81260_plan *plan)
{
    const u32 first_state6 = related_state_first == 6U ? 1U : 0U;
    const u32 state4 = related_state_first == 4U ? 1U : 0U;
    const u32 control_one = control_504dc8 == 1U ? 1U : 0U;
    const u32 second_state6 = related_state_second == 6U ? 1U : 0U;

    plan->related_state_first = related_state_first;
    plan->related_state_second = related_state_second;
    plan->control_504dc8 = control_504dc8;
    plan->result_table = 0x000728a0U;
    plan->result_value = result_value;
    plan->result_destination = first_state6 == 0U && state4 == 0U
        ? 0x00504d94U : 0U;
    plan->selector_value = state4 != 0U ? 7U : 0U;
    plan->first_state6_target = 0x00081414U;
    plan->state4_target = 0x000815d8U;
    plan->control_failure_target = 0x000815e0U;
    plan->second_state6_target = 0x00081470U;
    plan->common_target = 0x000815d4U;
    plan->target = first_state6 != 0U ? plan->first_state6_target :
                   state4 != 0U ? plan->state4_target :
                   control_one == 0U ? plan->control_failure_target :
                   second_state6 != 0U ? plan->second_state6_target :
                   plan->common_target;
}
