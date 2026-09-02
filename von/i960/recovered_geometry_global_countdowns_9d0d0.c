/* Persistent object countdown prefix recovered from i960 0x9d0d0-0x9d170. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_geometry_global_countdowns_plan {
    u32 frame_value;
    u32 counter_address[3];
    int32_t counter_before[3];
    u32 object_flag[3];
    int32_t counter_after[3];
};

void recovered_geometry_global_countdowns_plan(
    u32 frame_value, const u32 object_flag[3],
    const int32_t counter_before[3],
    struct recovered_geometry_global_countdowns_plan *plan)
{
    static const u32 addresses[3] = {
        0x00562c9cU, 0x00562ca0U, 0x00562ca4U,
    };

    plan->frame_value = frame_value;
    for (u32 i = 0; i != 3U; ++i) {
        plan->counter_address[i] = addresses[i];
        plan->counter_before[i] = counter_before[i];
        plan->object_flag[i] = object_flag[i] & 0xffU;

        /* A nonzero flag stores g14; otherwise cmpibge 0,counter
         * preserves nonpositive values and decrements positive values. */
        if (plan->object_flag[i] != 0U)
            plan->counter_after[i] = (int32_t)frame_value;
        else if (counter_before[i] > 0)
            plan->counter_after[i] = counter_before[i] - 1;
        else
            plan->counter_after[i] = counter_before[i];
    }
}
