/* Mirrored command-19 branch recovered from i960 0x9d59c-0x9d730. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_geometry_command19_mirror_branch {
    RECOVERED_GEOMETRY_COMMAND19_MIRROR_SPECIAL = 0,
    RECOVERED_GEOMETRY_COMMAND19_MIRROR_COUNTDOWN = 1,
    RECOVERED_GEOMETRY_COMMAND19_MIRROR_REARM = 2,
};

struct recovered_geometry_command19_mirror_plan {
    u32 fifo_address;
    u32 initial_packet_count;
    u32 initial_packet[4];
    u32 packet_count;
    u32 packet[4];
    u32 branch;
    u32 object_flag_1dd;
    u32 object_139_low;
    int32_t counter_94_before;
    int32_t counter_94_after;
    int32_t counter_a0;
    u32 frame_value;
    u32 helper_call_count;
    u32 helper_arg0[2];
    u32 helper_arg1[2];
    u32 helper_result_arg[2];
    u32 display_call;
    u32 display_source;
};

void recovered_geometry_command19_mirror_plan(
    u32 object_flag_1dd, u32 object_139_low,
    int32_t counter_94, int32_t counter_a0, u32 frame_value,
    u32 display_source, struct recovered_geometry_command19_mirror_plan *plan)
{
    plan->fifo_address = 0x00884000U;
    plan->initial_packet_count = 4U;
    plan->initial_packet[0] = 19U;
    plan->initial_packet[1] = 0xbe962fc9U;
    plan->initial_packet[2] = 0xbdf92c60U;
    plan->initial_packet[3] = 0x3f800000U;
    plan->packet_count = 4U;
    plan->packet[0] = 19U;
    plan->packet[1] = 0x3ada740eU;
    plan->packet[3] = 0x3f800000U;
    plan->branch = RECOVERED_GEOMETRY_COMMAND19_MIRROR_COUNTDOWN;
    plan->object_flag_1dd = object_flag_1dd & 0xffU;
    plan->object_139_low = object_139_low & 0xffU;
    plan->counter_94_before = counter_94;
    plan->counter_94_after = counter_94;
    plan->counter_a0 = counter_a0;
    plan->frame_value = frame_value;
    plan->helper_call_count = 0U;
    plan->display_call = 0U;
    plan->display_source = display_source;

    if (plan->object_flag_1dd == 0U && plan->object_139_low == 0U) {
        plan->branch = RECOVERED_GEOMETRY_COMMAND19_MIRROR_SPECIAL;
        plan->packet[2] = 0x3bc49ba6U;
        plan->counter_94_after = 30;
        if (counter_94 != 0) {
            plan->helper_call_count = 1U;
            plan->helper_arg0[0] = 7U;
            plan->helper_arg1[0] = 28U;
            plan->helper_result_arg[0] = 1U;
            plan->counter_94_after = (int32_t)frame_value;
        }
        return;
    }

    if (counter_94 != 0) {
        plan->packet[2] = 0x3bc49ba6U;
        return;
    }

    plan->branch = RECOVERED_GEOMETRY_COMMAND19_MIRROR_REARM;
    plan->packet[2] = 0x3b03126fU;
    if (counter_a0 != 0)
        return;

    plan->helper_call_count = 2U;
    plan->helper_arg0[0] = 7U;
    plan->helper_arg1[0] = 28U;
    plan->helper_result_arg[0] = 0U;
    plan->helper_arg0[1] = 9U;
    plan->helper_arg1[1] = 29U;
    plan->helper_result_arg[1] = 0U;
    plan->display_call = 0x01d210U;
    plan->counter_94_after = 1;
}
