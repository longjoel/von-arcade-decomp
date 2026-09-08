/* Geometry status dispatch recovered from i960 0x7e950-0x7e9f4. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_geometry_status_dispatch_7e950_plan {
    u32 original_status;
    u32 normalized_index;
    u32 table_target;
    u32 published_status;
    u32 control_504da4;
    u32 calls_79050;
    u32 action_destination;
    u32 action_value;
    u32 status_destination;
};

void recovered_state_geometry_status_dispatch_7e950(
    u32 status_504d94, u32 control_504da4,
    struct recovered_state_geometry_status_dispatch_7e950_plan *plan)
{
    static const u32 targets[12] = {
        0x0007e99cU, 0x0007e9b4U, 0x0007e9bcU, 0x0007e9c4U,
        0x0007e9c8U, 0x0007e9c8U, 0x0007e9c8U, 0x0007e9c8U,
        0x0007e9c8U, 0x0007e9c8U, 0x0007e9a4U, 0x0007e9acU
    };
    const u32 index = status_504d94 - 8U;
    u32 published = status_504d94;
    u32 target = 0x0007e9c8U;

    if (index <= 11U) {
        target = targets[index];
        if (index <= 3U)
            published = index + 1U;
        else if (index == 10U)
            published = 2U;
        else if (index == 11U)
            published = 3U;
    }

    plan->original_status = status_504d94;
    plan->normalized_index = index;
    plan->table_target = target;
    plan->published_status = published;
    plan->control_504da4 = control_504da4;
    plan->calls_79050 = control_504da4 == 1U ? 1U : 0U;
    plan->action_destination = 0x00504db8U;
    plan->action_value = 30U;
    plan->status_destination = 0x00504d94U;
}
