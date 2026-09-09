/* Runtime event arm 2 paired-delta prefix recovered from i960 0xe96b8-0xe9748. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 left_word_8;
    recovered_u32 left_word_10;
    recovered_u32 right_word_8;
    recovered_u32 right_word_10;
    recovered_u32 phase_before;
    recovered_u32 delta_word_10;
    recovered_u32 delta_word_8;
    recovered_u32 packet[6];
    recovered_u32 packet_count;
    recovered_u32 phase_after;
    recovered_u32 phase_address;
    recovered_u32 left_record_base;
    recovered_u32 right_record_base;
    recovered_u32 fifo_address;
    recovered_u32 delta_command;
    recovered_u32 paired_value_command;
    recovered_u32 next_target;
} recovered_geometry_runtime_event_arm2_prefix_result_e96b8;

recovered_geometry_runtime_event_arm2_prefix_result_e96b8
recovered_geometry_runtime_event_arm2_prefix_e96b8(
    recovered_u32 left_word_8, recovered_u32 left_word_10,
    recovered_u32 right_word_8, recovered_u32 right_word_10,
    recovered_u32 phase_before)
{
    recovered_geometry_runtime_event_arm2_prefix_result_e96b8 result;

    result.left_word_8 = left_word_8;
    result.left_word_10 = left_word_10;
    result.right_word_8 = right_word_8;
    result.right_word_10 = right_word_10;
    result.phase_before = phase_before;
    result.delta_word_10 = right_word_10 - left_word_10;
    result.delta_word_8 = right_word_8 - left_word_8;
    result.packet[0] = 10U;
    result.packet[1] = result.delta_word_10;
    result.packet[2] = result.delta_word_8;
    result.packet[3] = 31U;
    result.packet[4] = right_word_8;
    result.packet[5] = left_word_8;
    result.packet_count = 6U;
    result.phase_after = phase_before + 1U;
    result.phase_address = 0x005783e6U;
    result.left_record_base = 0x005040d0U;
    result.right_record_base = 0x00503ad0U;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.delta_command = 10U;
    result.paired_value_command = 31U;
    result.next_target = 0x000e974cU;
    return result;
}
