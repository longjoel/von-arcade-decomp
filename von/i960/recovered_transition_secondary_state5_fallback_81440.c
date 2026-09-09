/* State-5 fall-through continuation recovered from i960 0x81440-0x81480. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_secondary_state5_fallback_81440_plan {
    u32 control_504dc8;
    u32 object_state_64;
    u32 current_state_504d68;
    u32 result_table;
    u32 result_value;
    u32 result_destination;
    u32 published_status;
    u32 status_destination;
    u32 state6_status_target;
    u32 normal_target;
    u32 control_failure_target;
    u32 target;
};

void recovered_transition_secondary_state5_fallback_81440(
    u32 control_504dc8,
    u32 object_state_64,
    u32 current_state_504d68,
    u32 result_value,
    struct recovered_transition_secondary_state5_fallback_81440_plan *plan)
{
    const u32 control_one = control_504dc8 == 1U ? 1U : 0U;
    const u32 object_state6 = object_state_64 == 6U ? 1U : 0U;

    plan->control_504dc8 = control_504dc8;
    plan->object_state_64 = object_state_64;
    plan->current_state_504d68 = current_state_504d68;
    plan->result_table = 0x000728a0U;
    plan->result_value = result_value;
    plan->result_destination = 0x00504d94U;
    plan->published_status = control_one != 0U && object_state6 != 0U ? 9U : 0U;
    plan->status_destination = plan->published_status != 0U ? 0x00504d94U : 0U;
    plan->state6_status_target = 0x000815e0U;
    plan->normal_target = 0x000815d4U;
    plan->control_failure_target = 0x000815e0U;
    plan->target = control_one == 0U ? plan->control_failure_target :
                   object_state6 != 0U ? plan->state6_status_target :
                   plan->normal_target;
}
