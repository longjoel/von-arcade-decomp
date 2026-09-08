/* Action-25 publication tail recovered from i960 0x7e230-0x7e274. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_followup_action25_publication_7e230_plan {
    u32 classifier_index;
    u32 result_table;
    u32 result_value;
    u32 derived_value;
    u32 derived_destination;
    u32 control_destination;
    u32 control_value;
    u32 action_destination;
    u32 action_value;
    u32 continuation_destination;
    u32 continuation_value;
    u32 status_destination;
};

void recovered_state_followup_action25_publication_7e230(
    u32 classifier_index, u32 result_value, u32 caller_continuation,
    struct recovered_state_followup_action25_publication_7e230_plan *plan)
{
    plan->classifier_index = classifier_index;
    plan->result_table = 0x00072660U;
    plan->result_value = result_value;
    plan->derived_value = classifier_index - 1U;
    plan->derived_destination = 0x00504db4U;
    plan->control_destination = 0x00504d9cU;
    plan->control_value = 1U;
    plan->action_destination = 0x00504db8U;
    plan->action_value = 25U;
    plan->continuation_destination = 0x00504da0U;
    plan->continuation_value = caller_continuation;
    plan->status_destination = 0x00504d94U;
}
