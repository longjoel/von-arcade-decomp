/* Shared runtime event finalizer recovered from i960 0xea0b0-0xea19c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 record_word_8;
    recovered_u32 record_word_10;
    recovered_u32 state_3f0;
    recovered_u32 state_3f4;
    recovered_u32 state_3f8;
    recovered_u32 first_fifo_response;
    recovered_u32 second_fifo_response;
    recovered_u32 delta_word_10;
    recovered_u32 delta_word_8;
    recovered_u32 first_packet[3];
    recovered_u32 second_packet[7];
    recovered_u32 first_packet_count;
    recovered_u32 second_packet_count;
    recovered_u32 state_3e4;
    recovered_u32 fifo_address;
    recovered_u32 delta_command;
    recovered_u32 paired_value_command;
    recovered_u32 continuation_target;
} recovered_geometry_runtime_event_common_finalize_result_ea0b0;

recovered_geometry_runtime_event_common_finalize_result_ea0b0
recovered_geometry_runtime_event_common_finalize_ea0b0(
    recovered_u32 record_word_8, recovered_u32 record_word_10,
    recovered_u32 state_3f0, recovered_u32 state_3f4,
    recovered_u32 state_3f8, recovered_u32 first_fifo_response,
    recovered_u32 second_fifo_response)
{
    recovered_geometry_runtime_event_common_finalize_result_ea0b0 result;

    result.record_word_8 = record_word_8;
    result.record_word_10 = record_word_10;
    result.state_3f0 = state_3f0;
    result.state_3f4 = state_3f4;
    result.state_3f8 = state_3f8;
    result.first_fifo_response = first_fifo_response;
    result.second_fifo_response = second_fifo_response;
    result.delta_word_10 = record_word_10 - state_3f8;
    result.delta_word_8 = record_word_8 - state_3f4;
    result.first_packet[0] = 10U;
    result.first_packet[1] = result.delta_word_10;
    result.first_packet[2] = result.delta_word_8;
    result.second_packet[0] = 31U;
    result.second_packet[1] = state_3f4;
    result.second_packet[2] = record_word_8;
    result.second_packet[3] = 0U;
    result.second_packet[4] = 0U;
    result.second_packet[5] = state_3f8;
    result.second_packet[6] = record_word_10;
    result.first_packet_count = 3U;
    result.second_packet_count = 7U;
    result.state_3e4 = first_fifo_response;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.delta_command = 10U;
    result.paired_value_command = 31U;
    result.continuation_target = 0x000ea6fcU;
    return result;
}
