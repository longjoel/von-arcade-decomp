/* Special status publication recovered from i960 0x7f44c-0x7f4c4. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state31_special_status_publication_7f44c_plan {
    u32 incoming_status;
    u32 related_state;
    u32 accepted;
    u32 admission_arm;
    u32 selector_destination;
    u32 selector_value;
    u32 status_destination;
    u32 status_value;
    u32 control_destination;
    u32 control_value;
    u32 callback_target;
    u32 callback_argument;
    u32 action_destination;
    u32 action_value;
    u32 target;
    u32 failure_target;
};

void recovered_state31_special_status_publication_7f44c(
    u32 incoming_status, u32 related_state, u32 related_pointer,
    struct recovered_state31_special_status_publication_7f44c_plan *plan)
{
    u32 arm = 0U;
    if (incoming_status == 0x92U && related_state == 6U)
        arm = 1U;
    else if (incoming_status == 0x44U)
        arm = 2U;
    else if (incoming_status == 0x56U && related_state == 7U)
        arm = 3U;
    else if (incoming_status == 0x57U && related_state == 7U)
        arm = 4U;

    plan->incoming_status = incoming_status;
    plan->related_state = related_state;
    plan->accepted = arm != 0U ? 1U : 0U;
    plan->admission_arm = arm;
    plan->selector_destination = arm ? 0x00504d9cU : 0U;
    plan->selector_value = arm ? 3U : 0U;
    plan->status_destination = arm ? 0x00504d94U : 0U;
    plan->status_value = arm ? 7U : 0U;
    plan->control_destination = arm ? 0x00504da0U : 0U;
    plan->control_value = arm ? incoming_status : 0U;
    plan->callback_target = arm ? 0x00079d60U : 0U;
    plan->callback_argument = arm ? related_pointer : 0U;
    plan->action_destination = arm ? 0x00504db8U : 0U;
    plan->action_value = arm ? 30U : 0U;
    plan->target = arm ? 0x0007f4c0U : 0x0007f4c4U;
    plan->failure_target = 0x0007f4c4U;
}
