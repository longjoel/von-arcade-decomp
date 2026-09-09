/* Status publication tail recovered from i960 0x80650-0x806f4. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_geometry_status_tail_80650_plan {
    u32 publication_gate_passed;
    u32 incoming_status;
    u32 status_minus_8;
    u32 mapped_status;
    u32 callback_enable;
    u32 callback_target;
    u32 callback_argument;
    u32 status_destination;
    u32 action_destination;
    u32 action_value;
    u32 return_value;
    u32 target;
};

/*
 * The floating admission preceding 0x80650 is the caller's control-flow
 * responsibility; entry here is already the admitted path.  The table at
 * 0x8066c rewrites only indices 0,1,2,3,10,11; all other indices reach the
 * common tail with the original status still in g5.
 */
void recovered_geometry_status_tail_80650(
    u32 incoming_status,
    u32 global_callback_enable,
    u32 callback_argument,
    struct recovered_geometry_status_tail_80650_plan *plan)
{
    const u32 index = incoming_status - 8U;
    const u32 admitted = 1U;
    const u32 callback = global_callback_enable == 1U
        ? 1U : 0U;
    u32 mapped_status = incoming_status;

    switch (index) {
    case 0U:
        mapped_status = 1U;
        break;
    case 1U:
        mapped_status = 4U;
        break;
    case 2U:
        mapped_status = 5U;
        break;
    case 3U:
        mapped_status = 6U;
        break;
    case 10U:
        mapped_status = 2U;
        break;
    case 11U:
        mapped_status = 3U;
        break;
    default:
        break;
    }

    plan->publication_gate_passed = admitted;
    plan->incoming_status = incoming_status;
    plan->status_minus_8 = index;
    plan->mapped_status = mapped_status;
    plan->callback_enable = callback;
    plan->callback_target = callback != 0U ? 0x00079050U : 0U;
    plan->callback_argument = callback != 0U ? callback_argument : 0U;
    plan->status_destination = 0x00504d94U;
    plan->action_destination = 0x00504db8U;
    plan->action_value = 30U;
    plan->return_value = 1U;
    plan->target = 0x000806f4U;
}
