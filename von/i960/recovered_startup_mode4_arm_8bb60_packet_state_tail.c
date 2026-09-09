/* Selector-1 packet/state tail recovered from i960 0x8bb60-0x8bd60. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 command_31_word;
    recovered_u32 first_command_10_word_1;
    recovered_u32 first_command_10_word_2;
    recovered_u32 second_command_10_word_1;
    recovered_u32 second_command_10_word_2;
    recovered_u32 rolling_51c958;
    recovered_u32 rolling_51c95c;
    recovered_u32 rolling_51c960;
    recovered_u32 state_51c94c;
    recovered_u32 command_31_response;
    recovered_u32 first_command_10_response;
    recovered_u32 second_command_10_response;
    recovered_u32 record_30;
    recovered_u32 command_31_packet[2];
    recovered_u32 command_10_packet_0[3];
    recovered_u32 command_10_packet_1[3];
    recovered_u32 state_51c940;
    recovered_u32 state_51c944;
    recovered_u32 fifo_address;
    recovered_u32 command_31;
    recovered_u32 command_10;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8bb60_packet_state_tail_result;

recovered_startup_mode4_arm_8bb60_packet_state_tail_result
recovered_startup_mode4_arm_8bb60_packet_state_tail(
    recovered_u32 command_31_word, recovered_u32 first_command_10_word_1,
    recovered_u32 first_command_10_word_2, recovered_u32 second_command_10_word_1,
    recovered_u32 second_command_10_word_2, recovered_u32 rolling_51c958,
    recovered_u32 rolling_51c95c, recovered_u32 rolling_51c960,
    recovered_u32 state_51c94c, recovered_u32 command_31_response,
    recovered_u32 first_command_10_response,
    recovered_u32 second_command_10_response, recovered_u32 record_30)
{
    recovered_startup_mode4_arm_8bb60_packet_state_tail_result result;

    result.command_31_word = command_31_word;
    result.first_command_10_word_1 = first_command_10_word_1;
    result.first_command_10_word_2 = first_command_10_word_2;
    result.second_command_10_word_1 = second_command_10_word_1;
    result.second_command_10_word_2 = second_command_10_word_2;
    result.rolling_51c958 = rolling_51c958;
    result.rolling_51c95c = rolling_51c95c;
    result.rolling_51c960 = rolling_51c960;
    result.state_51c94c = state_51c94c;
    result.command_31_response = command_31_response;
    result.first_command_10_response = first_command_10_response;
    result.second_command_10_response = second_command_10_response;
    result.record_30 = record_30;
    result.command_31_packet[0] = 31U;
    result.command_31_packet[1] = command_31_word;
    result.command_10_packet_0[0] = 10U;
    result.command_10_packet_0[1] = first_command_10_word_1;
    result.command_10_packet_0[2] = first_command_10_word_2;
    result.command_10_packet_1[0] = 10U;
    result.command_10_packet_1[1] = second_command_10_word_1;
    result.command_10_packet_1[2] = second_command_10_word_2;
    result.state_51c940 = first_command_10_response;
    result.state_51c944 = second_command_10_response;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.command_31 = 31U;
    result.command_10 = 10U;
    result.continuation = record_30 == 0U ? 0x0008bd60U : 0x0008bfacU;
    return result;
}
