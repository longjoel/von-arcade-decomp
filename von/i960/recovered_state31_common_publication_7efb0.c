/* Common state-31 publication recovered from i960 0x7efb0-0x7efec. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state31_common_publication_7efb0_plan {
    u32 classifier_band;
    u32 result_table;
    u32 result_value;
    u32 status_destination;
    u32 callback_target;
    u32 callback_argument;
    u32 action_destination;
    u32 action_value;
    u32 control_destination;
    u32 control_value;
    u32 selector_destination;
    u32 selector_value;
    u32 returns;
};

void recovered_state31_common_publication_7efb0(
    u32 classifier_band, u32 result_value, u32 related_pointer,
    struct recovered_state31_common_publication_7efb0_plan *plan)
{
    plan->classifier_band = classifier_band;
    plan->result_table = 0x0072780U;
    plan->result_value = result_value;
    plan->status_destination = 0x00504d94U;
    plan->callback_target = 0x00079050U;
    plan->callback_argument = related_pointer;
    plan->action_destination = 0x00504db8U;
    plan->action_value = 30U;
    plan->control_destination = 0x00504d9cU;
    plan->control_value = 3U;
    plan->selector_destination = 0x00504da0U;
    plan->selector_value = 0x64U;
    plan->returns = 1U;
}
