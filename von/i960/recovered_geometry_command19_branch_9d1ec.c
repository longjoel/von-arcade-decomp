/* Command-19 branch recovered from i960 0x9d1ec-0x9d334. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_geometry_command19_branch {
    RECOVERED_GEOMETRY_COMMAND19_SPECIAL = 0,
    RECOVERED_GEOMETRY_COMMAND19_COUNTDOWN = 1,
    RECOVERED_GEOMETRY_COMMAND19_REARM = 2,
};

struct recovered_geometry_command19_branch_plan {
    u32 fifo_address;
    u32 packet_count;
    u32 packet[4];
    u32 branch;
    u32 object_flag_1de;
    u32 object_138_low;
    int32_t counter_90_before;
    int32_t counter_90_after;
    int32_t counter_9c;
    u32 frame_value;
    u32 helper_call_count;
    u32 helper_arg0[2];
    u32 helper_arg1[2];
    u32 helper_result_arg[2];
    u32 display_call;
    u32 display_source;
};

void recovered_geometry_command19_branch_plan(
    u32 object_flag_1de, u32 object_138_low,
    int32_t counter_90, int32_t counter_9c, u32 frame_value,
    u32 display_source,
    struct recovered_geometry_command19_branch_plan *plan)
{
    plan->fifo_address = 0x00884000U;
    plan->packet_count = 4U;
    plan->packet[0] = 19U;
    plan->packet[1] = 0x3ada740eU;
    plan->packet[3] = 0x3f800000U;
    plan->branch = RECOVERED_GEOMETRY_COMMAND19_COUNTDOWN;
    plan->object_flag_1de = object_flag_1de & 0xffU;
    plan->object_138_low = object_138_low & 0xffU;
    plan->counter_90_before = counter_90;
    plan->counter_90_after = counter_90;
    plan->counter_9c = counter_9c;
    plan->frame_value = frame_value;
    plan->helper_call_count = 0U;
    plan->display_call = 0U;
    plan->display_source = display_source;

    /* The first path requires both object tests to be zero. */
    if (plan->object_flag_1de == 0U && plan->object_138_low == 0U) {
        plan->branch = RECOVERED_GEOMETRY_COMMAND19_SPECIAL;
        plan->packet[2] = 0x3bc49ba6U;
        plan->counter_90_after = 30;
        if (counter_90 != 0) {
            plan->helper_call_count = 1U;
            plan->helper_arg0[0] = 39U; /* 31+8 */
            plan->helper_arg1[0] = 28U;
            plan->helper_result_arg[0] = 1U;
            plan->counter_90_after = (int32_t)frame_value;
        }
        return;
    }

    if (counter_90 != 0) {
        plan->packet[2] = 0x3bc49ba6U;
        return;
    }

    plan->branch = RECOVERED_GEOMETRY_COMMAND19_REARM;
    plan->packet[2] = 0x3b03126fU;
    if (counter_9c != 0)
        return;

    plan->helper_call_count = 2U;
    plan->helper_arg0[0] = 39U; /* 31+8 */
    plan->helper_arg1[0] = 28U;
    plan->helper_result_arg[0] = 0U;
    plan->helper_arg0[1] = 43U; /* 31+12 */
    plan->helper_arg1[1] = 29U;
    plan->helper_result_arg[1] = 0U;
    plan->display_call = 0x01d210U;
    plan->counter_90_after = 1;
}
