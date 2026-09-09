/* Selector-0 response tail recovered from i960 0x8c16c-0x8c2cc. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 adjusted_operand;
    recovered_u32 helper_result;
    recovered_u32 selected_float;
    recovered_u32 adjusted_float;
    recovered_u32 timing_5770f0;
    recovered_u32 first_command_10_word_1;
    recovered_u32 first_command_10_word_2;
    recovered_u32 second_command_10_word_1;
    recovered_u32 second_command_10_word_2;
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
} recovered_startup_mode4_arm_8c16c_response_tail_result;

recovered_startup_mode4_arm_8c16c_response_tail_result
recovered_startup_mode4_arm_8c16c_response_tail(
    recovered_u32 adjusted_operand, recovered_u32 helper_result,
    recovered_u32 selected_float, recovered_u32 adjusted_float,
    recovered_u32 timing_5770f0, recovered_u32 first_command_10_word_1,
    recovered_u32 first_command_10_word_2, recovered_u32 second_command_10_word_1,
    recovered_u32 second_command_10_word_2, recovered_u32 first_response,
    recovered_u32 second_response, recovered_u32 state_51c948,
    recovered_u32 record_30)
{
    recovered_startup_mode4_arm_8c16c_response_tail_result result;

    result.adjusted_operand = adjusted_operand;
    result.helper_result = helper_result;
    result.selected_float = selected_float;
    result.adjusted_float = adjusted_float;
    result.timing_5770f0 = timing_5770f0;
    result.first_command_10_word_1 = first_command_10_word_1;
    result.first_command_10_word_2 = first_command_10_word_2;
    result.second_command_10_word_1 = second_command_10_word_1;
    result.second_command_10_word_2 = second_command_10_word_2;
    result.first_response = first_response;
    result.second_response = second_response;
    result.state_51c948 = state_51c948;
    result.record_30 = record_30;
    result.command_10_packet_0[0] = 10U;
    result.command_10_packet_0[1] = first_command_10_word_1;
    result.command_10_packet_0[2] = first_command_10_word_2;
    result.command_10_packet_1[0] = 10U;
    result.command_10_packet_1[1] = second_command_10_word_1;
    result.command_10_packet_1[2] = second_command_10_word_2;
    result.state_51c940 = first_response;
    result.state_51c944 = second_response;
    result.state_51c94c = second_command_10_word_2;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.command = 10U;
    result.continuation = record_30 == 0U ? 0x0008c904U : 0x0008c8f4U;
    return result;
}
