/* Runtime event arm 4 delta prefix recovered from i960 0xea1a0-0xea1f8. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 left_word_8;
    recovered_u32 left_word_10;
    recovered_u32 right_word_8;
    recovered_u32 right_word_10;
    recovered_u32 event_count;
    recovered_u32 fifo_response;
    recovered_u32 delta_word_10;
    recovered_u32 delta_word_8;
    recovered_u32 packet[3];
    recovered_u32 packet_count;
    recovered_u32 state_3e4;
    recovered_u32 state_address;
    recovered_u32 fifo_address;
    recovered_u32 threshold;
    recovered_u32 extended_path;
    recovered_u32 short_path_target;
    recovered_u32 extended_path_target;
} recovered_geometry_runtime_event_arm4_prefix_result_ea1a0;

recovered_geometry_runtime_event_arm4_prefix_result_ea1a0
recovered_geometry_runtime_event_arm4_prefix_ea1a0(
    recovered_u32 left_word_8, recovered_u32 left_word_10,
    recovered_u32 right_word_8, recovered_u32 right_word_10,
    recovered_u32 event_count, recovered_u32 fifo_response)
{
    recovered_geometry_runtime_event_arm4_prefix_result_ea1a0 result;

    result.left_word_8 = left_word_8;
    result.left_word_10 = left_word_10;
    result.right_word_8 = right_word_8;
    result.right_word_10 = right_word_10;
    result.event_count = event_count;
    result.fifo_response = fifo_response;
    result.delta_word_10 = right_word_10 - left_word_10;
    result.delta_word_8 = left_word_8 - right_word_8;
    result.packet[0] = 10U;
    result.packet[1] = result.delta_word_10;
    result.packet[2] = result.delta_word_8;
    result.packet_count = 3U;
    result.state_3e4 = fifo_response;
    result.state_address = 0x005783e4U;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.threshold = 44U;
    result.extended_path = event_count > result.threshold;
    result.short_path_target = 0x000ea1f8U;
    result.extended_path_target = 0x000ea2b8U;
    return result;
}
