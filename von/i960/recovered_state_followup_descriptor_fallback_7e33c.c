/* Descriptor-helper fallback recovered from i960 0x7e33c-0x7e384. */
#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_state_followup_descriptor_fallback_7e33c_plan {
    u32 helper_target;
    u32 helper_result;
    u32 restored_control;
    u32 restored_selector;
    u32 restored_action;
    u32 writes_status;
    u32 status_destination;
    u32 status_value;
    u32 control_destination;
    u32 selector_destination;
    u32 action_destination;
};

void recovered_state_followup_descriptor_fallback_7e33c(
    u32 helper_result, u32 saved_control, u32 saved_selector,
    u32 saved_action, s32 global_504dc4,
    struct recovered_state_followup_descriptor_fallback_7e33c_plan *plan)
{
    plan->helper_target = 0x0007e390U;
    plan->helper_result = helper_result;
    plan->restored_control = 0U;
    plan->restored_selector = 0U;
    plan->restored_action = 0U;
    plan->writes_status = 0U;
    plan->status_destination = 0U;
    plan->status_value = 0U;
    plan->control_destination = 0U;
    plan->selector_destination = 0U;
    plan->action_destination = 0U;

    if (helper_result == 0U) {
        plan->restored_control = saved_control;
        plan->restored_selector = saved_selector;
        plan->restored_action = saved_action;
        plan->control_destination = 0x00504d9cU;
        plan->selector_destination = 0x00504da0U;
        plan->action_destination = 0x00504db4U;
    } else if (global_504dc4 < -15) {
        plan->writes_status = 1U;
        plan->status_destination = 0x00504d94U;
        plan->status_value = 4U;
    }
}
