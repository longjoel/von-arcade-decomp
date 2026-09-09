/* Selector-0 response tail recovered from i960 0x8b85c-0x8b944. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 packet_word_1;
    recovered_u32 packet_word_2;
    recovered_u32 computed_word;
    recovered_u32 first_response;
    recovered_u32 second_response;
    recovered_u32 state_51c948;
    recovered_u32 record_30;
    recovered_u32 command_10_packet_0[3];
    recovered_u32 command_10_packet_1[3];
    recovered_u32 state_51c940;
    recovered_u32 state_51c944;
    recovered_u32 state_51c94c;
    recovered_u32 fifo_address;
    recovered_u32 command;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8b85c_response_tail_result;

recovered_startup_mode4_arm_8b85c_response_tail_result
recovered_startup_mode4_arm_8b85c_response_tail(
    recovered_u32 packet_word_1, recovered_u32 packet_word_2,
    recovered_u32 computed_word, recovered_u32 first_response,
    recovered_u32 second_response, recovered_u32 state_51c948,
    recovered_u32 record_30)
{
    recovered_startup_mode4_arm_8b85c_response_tail_result result;

    result.packet_word_1 = packet_word_1;
    result.packet_word_2 = packet_word_2;
    result.computed_word = computed_word;
    result.first_response = first_response;
    result.second_response = second_response;
    result.state_51c948 = state_51c948;
    result.record_30 = record_30;
    result.command_10_packet_0[0] = 10U;
    result.command_10_packet_0[1] = packet_word_1;
    result.command_10_packet_0[2] = packet_word_2;
    result.command_10_packet_1[0] = 10U;
    result.command_10_packet_1[1] = state_51c948;
    result.command_10_packet_1[2] = computed_word;
    result.state_51c940 = first_response;
    result.state_51c944 = second_response;
    result.state_51c94c = 0U;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.command = 10U;
    result.continuation = record_30 == 0U ? 0x0008bfacU : 0x0008bd60U;
    return result;
}
