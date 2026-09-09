/* Selector-5 state/packet sequence recovered from i960 0x89814-0x89930. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 record_8;
    recovered_u32 record_10;
    recovered_u32 record_0c;
    recovered_u32 prior_51c958;
    recovered_u32 prior_51c95c;
    recovered_u32 prior_51c960;
    recovered_u32 first_fifo_response;
    recovered_u32 computed_second_command_word;
    recovered_u32 second_fifo_response;
    recovered_u32 first_command_packet[3];
    recovered_u32 command_31_packet[7];
    recovered_u32 second_command_packet[3];
    recovered_u32 state_51c940;
    recovered_u32 state_51c944;
    recovered_u32 state_51c94c;
    recovered_u32 state_51c950;
    recovered_u32 state_51c954;
    recovered_u32 fifo_address;
    recovered_u32 first_command;
    recovered_u32 second_command;
    recovered_u32 third_command;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_89814_state_packet_sequence_result;

recovered_startup_mode4_arm_89814_state_packet_sequence_result
recovered_startup_mode4_arm_89814_state_packet_sequence(
    recovered_u32 record_8, recovered_u32 record_10,
    recovered_u32 prior_51c958, recovered_u32 prior_51c95c,
    recovered_u32 prior_51c960, recovered_u32 first_fifo_response,
    recovered_u32 record_0c, recovered_u32 second_fifo_response,
    recovered_u32 state_51c948)
{
    recovered_startup_mode4_arm_89814_state_packet_sequence_result result;

    result.record_8 = record_8;
    result.record_10 = record_10;
    result.record_0c = record_0c;
    result.prior_51c958 = prior_51c958;
    result.prior_51c95c = prior_51c95c;
    result.prior_51c960 = prior_51c960;
    result.first_fifo_response = first_fifo_response;
    result.computed_second_command_word = prior_51c95c - record_0c;
    result.second_fifo_response = second_fifo_response;
    result.first_command_packet[0] = 10U;
    result.first_command_packet[1] = record_10 - prior_51c960;
    result.first_command_packet[2] = record_8 - prior_51c958;
    result.command_31_packet[0] = 31U;
    result.command_31_packet[1] = prior_51c958;
    result.command_31_packet[2] = record_8;
    result.command_31_packet[3] = 0U;
    result.command_31_packet[4] = 0U;
    result.command_31_packet[5] = prior_51c960;
    result.command_31_packet[6] = record_10;
    result.second_command_packet[0] = 10U;
    result.second_command_packet[1] = state_51c948;
    result.second_command_packet[2] = result.computed_second_command_word;
    result.state_51c940 = first_fifo_response;
    result.state_51c944 = second_fifo_response;
    result.state_51c94c = prior_51c95c;
    result.state_51c950 = prior_51c958;
    result.state_51c954 = prior_51c960;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.first_command = 10U;
    result.second_command = 31U;
    result.third_command = 10U;
    result.continuation = 0x00089930U;
    return result;
}
