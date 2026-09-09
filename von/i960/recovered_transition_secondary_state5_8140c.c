/* State-5 secondary body recovered from i960 0x8140c-0x81440. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_secondary_state5_8140c_plan {
    u32 object_state_64;
    u32 current_state_504d68;
    u32 result_table;
    u32 result_value;
    u32 result_destination;
    u32 selector_value;
    u32 selector_destination;
    u32 state6_target;
    u32 state4_result_target;
    u32 state4_return_target;
    u32 target;
};

void recovered_transition_secondary_state5_8140c(
    u32 object_state_64,
    u32 current_state_504d68,
    u32 result_value,
    struct recovered_transition_secondary_state5_8140c_plan *plan)
{
    plan->object_state_64 = object_state_64;
    plan->current_state_504d68 = current_state_504d68;
    plan->result_table = object_state_64 == 6U ? 0x00072750U : 0U;
    plan->result_value = result_value;
    plan->result_destination = object_state_64 == 6U ? 0x00504d94U : 0U;
    plan->selector_value = object_state_64 == 4U ? 7U : 0U;
    plan->selector_destination = object_state_64 == 4U ? 0x00504d94U : 0U;
    plan->state6_target = 0x00081440U;
    plan->state4_result_target = 0x000815e0U;
    plan->state4_return_target = 0x000815d8U;
    plan->target = object_state_64 == 6U ? plan->state4_result_target :
                   object_state_64 == 4U ? plan->state4_return_target :
                   plan->state6_target;
}
