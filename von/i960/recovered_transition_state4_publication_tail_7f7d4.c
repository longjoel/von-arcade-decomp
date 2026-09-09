/* State-4 publication tail recovered from i960 0x7f7d4-0x7f7fc. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_state4_publication_tail_7f7d4_plan {
    u32 classifier_result;
    u32 callback_gate;
    u32 related_pointer;
    u32 status_destination;
    u32 published_status;
    u32 callback_target;
    u32 callback_argument;
    u32 action_destination;
    u32 action_value;
    u32 target;
};

void recovered_transition_state4_publication_tail_7f7d4(
    u32 classifier_result, u32 callback_gate, u32 related_pointer,
    struct recovered_transition_state4_publication_tail_7f7d4_plan *plan)
{
    plan->classifier_result = classifier_result;
    plan->callback_gate = callback_gate;
    plan->related_pointer = related_pointer;
    plan->status_destination = 0x00504d94U;
    plan->published_status = classifier_result;
    plan->callback_target = callback_gate == 1U ? 0x00079050U : 0U;
    plan->callback_argument = callback_gate == 1U ? related_pointer : 0U;
    plan->action_destination = 0x00504db8U;
    plan->action_value = 30U;
    plan->target = 0x0007f7fcU;
}
