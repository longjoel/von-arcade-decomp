/* Third mirrored command-19 branch recovered from i960 0x9d9a0-0x9db3c. */
#include <stdint.h>

typedef uint32_t u32;

enum recovered_geometry_command19_third_branch {
    RECOVERED_GEOMETRY_COMMAND19_THIRD_SPECIAL = 0,
    RECOVERED_GEOMETRY_COMMAND19_THIRD_COUNTDOWN = 1,
    RECOVERED_GEOMETRY_COMMAND19_THIRD_REARM = 2,
};

struct recovered_geometry_command19_third_plan {
    u32 fifo_address;
    u32 initial_packet_count;
    u32 initial_packet[4];
    u32 packet_count;
    u32 packet[4];
    u32 branch;
    u32 object_flag_1df;
    u32 object_13a_low;
    int32_t counter_a4_before;
    int32_t counter_a4_after;
    int32_t counter_98;
    u32 frame_value;
    u32 helper_call_count;
    u32 helper_arg0[2];
    u32 helper_arg1[2];
    u32 helper_result_arg[2];
    u32 display_call;
    u32 display_source;
};

void recovered_geometry_command19_third_plan(
    u32 object_flag_1df, u32 object_13a_low,
    int32_t counter_a4, int32_t counter_98, u32 frame_value,
    u32 display_source, struct recovered_geometry_command19_third_plan *plan)
{
    plan->fifo_address = 0x00884000U;
    plan->initial_packet_count = 4U;
    plan->initial_packet[0] = 19U;
    plan->initial_packet[1] = 0xbd888889U;
    plan->initial_packet[2] = 0xbdf92c60U;
    plan->initial_packet[3] = 0x3f800000U;
    plan->packet_count = 4U;
    plan->packet[0] = 19U;
    plan->packet[1] = 0x3ada740eU;
    plan->packet[3] = 0x3f800000U;
    plan->branch = RECOVERED_GEOMETRY_COMMAND19_THIRD_COUNTDOWN;
    plan->object_flag_1df = object_flag_1df & 0xffU;
    plan->object_13a_low = object_13a_low & 0xffU;
    plan->counter_a4_before = counter_a4;
    plan->counter_a4_after = counter_a4;
    plan->counter_98 = counter_98;
    plan->frame_value = frame_value;
    plan->helper_call_count = 0U;
    plan->display_call = 0U;
    plan->display_source = display_source;

    if (plan->object_flag_1df == 0U && plan->object_13a_low == 0U) {
        plan->branch = RECOVERED_GEOMETRY_COMMAND19_THIRD_SPECIAL;
        plan->packet[2] = 0x3bc49ba6U;
        plan->counter_a4_after = 30;
        if (counter_a4 != 0) {
            plan->helper_call_count = 1U;
            plan->helper_arg0[0] = 23U;
            plan->helper_arg1[0] = 28U;
            plan->helper_result_arg[0] = 1U;
            plan->counter_a4_after = (int32_t)frame_value;
        }
        return;
    }

    if (counter_a4 != 0) {
        plan->packet[2] = 0x3bc49ba6U;
        return;
    }

    plan->branch = RECOVERED_GEOMETRY_COMMAND19_THIRD_REARM;
    plan->packet[2] = 0x3b03126fU;
    if (counter_98 != 0)
        return;

    plan->helper_call_count = 2U;
    plan->helper_arg0[0] = 23U;
    plan->helper_arg1[0] = 28U;
    plan->helper_result_arg[0] = 0U;
    plan->helper_arg0[1] = 26U;
    plan->helper_arg1[1] = 29U;
    plan->helper_result_arg[1] = 0U;
    plan->display_call = 0x01d210U;
    plan->counter_a4_after = 1;
}
