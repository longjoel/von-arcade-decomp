/* Selector-3 response tail recovered from i960 0x8a7e4-0x8a880. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 command_31_response;
    recovered_u32 computed_packet_word;
    recovered_u32 first_command_10_response;
    recovered_u32 second_command_10_response;
    recovered_u32 record_30;
    recovered_u32 command_10_packet[3];
    recovered_u32 state_51c940;
    recovered_u32 state_51c944;
    recovered_u32 fifo_address;
    recovered_u32 command;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8a7e4_response_tail_result;

recovered_startup_mode4_arm_8a7e4_response_tail_result
recovered_startup_mode4_arm_8a7e4_response_tail(
    recovered_u32 command_31_response, recovered_u32 computed_packet_word,
    recovered_u32 first_command_10_response,
    recovered_u32 second_command_10_response, recovered_u32 record_30)
{
    recovered_startup_mode4_arm_8a7e4_response_tail_result result;

    result.command_31_response = command_31_response;
    result.computed_packet_word = computed_packet_word;
    result.first_command_10_response = first_command_10_response;
    result.second_command_10_response = second_command_10_response;
    result.record_30 = record_30;
    result.command_10_packet[0] = 10U;
    result.command_10_packet[1] = first_command_10_response;
    result.command_10_packet[2] = computed_packet_word;
    result.state_51c940 = command_31_response;
    result.state_51c944 = second_command_10_response;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.command = 10U;
    result.continuation = record_30 == 0U ? 0x0008a16cU : 0x0008a880U;
    return result;
}
