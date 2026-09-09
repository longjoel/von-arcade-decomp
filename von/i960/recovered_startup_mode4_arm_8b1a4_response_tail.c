/* Selector-2 post-dispatch response tail recovered from i960 0x8b1a4-0x8b21c. */
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
    recovered_u32 state_51c950;
    recovered_u32 state_51c954;
    recovered_u32 fifo_address;
    recovered_u32 command;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8b1a4_response_tail_result;

recovered_startup_mode4_arm_8b1a4_response_tail_result
recovered_startup_mode4_arm_8b1a4_response_tail(
    recovered_u32 command_31_response, recovered_u32 computed_packet_word,
    recovered_u32 first_command_10_response,
    recovered_u32 second_command_10_response, recovered_u32 state_51c950,
    recovered_u32 state_51c954, recovered_u32 record_30)
{
    recovered_startup_mode4_arm_8b1a4_response_tail_result result;

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
    result.state_51c950 = state_51c950;
    result.state_51c954 = state_51c954;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.command = 10U;
    result.continuation = record_30 == 0U ? 0x0008aeccU : 0x0008b604U;
    return result;
}
