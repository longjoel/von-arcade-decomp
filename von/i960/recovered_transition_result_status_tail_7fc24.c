/* Result status tail recovered from i960 0x7fc24-0x7fc90. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_transition_result_status_tail_7fc24_plan {
    u32 current_status;
    u32 callback_gate;
    u32 related_pointer;
    u32 normalized_index;
    u32 table_target;
    u32 published_status;
    u32 callback_target;
    u32 callback_argument;
    u32 action_destination;
    u32 action_value;
    u32 target;
};

void recovered_transition_result_status_tail_7fc24(
    u32 current_status, u32 callback_gate, u32 related_pointer,
    struct recovered_transition_result_status_tail_7fc24_plan *plan)
{
    static const u32 targets[12] = {
        0x0007fc24U, 0x0007fc4cU, 0x0007fc54U, 0x0007fc64U,
        0x0007fc70U, 0x0007fc70U, 0x0007fc70U, 0x0007fc70U,
        0x0007fc70U, 0x0007fc70U, 0x0007fc34U, 0x0007fc3cU
    };
    const u32 index = current_status - 8U;
    u32 published = current_status;
    u32 table_target = 0x0007fc70U;

    if (index <= 11U) {
        table_target = targets[index];
        if (index <= 3U)
            published = index + 1U;
        else if (index == 10U)
            published = 2U;
        else if (index == 11U)
            published = 3U;
    }

    plan->current_status = current_status;
    plan->callback_gate = callback_gate;
    plan->related_pointer = related_pointer;
    plan->normalized_index = index;
    plan->table_target = table_target;
    plan->published_status = published;
    plan->callback_target = callback_gate == 1U ? 0x00079050U : 0U;
    plan->callback_argument = callback_gate == 1U ? related_pointer : 0U;
    plan->action_destination = 0x00504db8U;
    plan->action_value = 30U;
    plan->target = 0x0007fc90U;
}
