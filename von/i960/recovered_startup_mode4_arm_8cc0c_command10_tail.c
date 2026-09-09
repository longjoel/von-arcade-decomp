/* Selector-0 command/response tail recovered from i960 0x8cc0c-0x8ccfc. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 state_51c950;
    recovered_u32 state_51c954;
    recovered_u32 state_51c948;
    recovered_u32 computed_state_51c94c;
    recovered_u32 command_10_word_0;
    recovered_u32 command_10_word_1;
    recovered_u32 command_10_word_2;
    recovered_u32 first_response;
    recovered_u32 second_response;
    recovered_u32 record_30;
    recovered_u32 command_10_packet_0[3];
    recovered_u32 command_10_packet_1[3];
    recovered_u32 state_51c940;
    recovered_u32 state_51c944;
    recovered_u32 state_51c94c;
    recovered_u32 fifo_address;
    recovered_u32 command_10;
    recovered_u32 record_zero_path;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8cc0c_command10_tail_result;

recovered_startup_mode4_arm_8cc0c_command10_tail_result
recovered_startup_mode4_arm_8cc0c_command10_tail(
    recovered_u32 state_51c950, recovered_u32 state_51c954,
    recovered_u32 state_51c948, recovered_u32 computed_state_51c94c,
    recovered_u32 command_10_word_0, recovered_u32 command_10_word_1,
    recovered_u32 command_10_word_2, recovered_u32 first_response,
    recovered_u32 second_response, recovered_u32 record_30)
{
    recovered_startup_mode4_arm_8cc0c_command10_tail_result result;

    result.state_51c950 = state_51c950;
    result.state_51c954 = state_51c954;
    result.state_51c948 = state_51c948;
    result.computed_state_51c94c = computed_state_51c94c;
    result.command_10_word_0 = command_10_word_0;
    result.command_10_word_1 = command_10_word_1;
    result.command_10_word_2 = command_10_word_2;
    result.first_response = first_response;
    result.second_response = second_response;
    result.record_30 = record_30;
    result.command_10_packet_0[0] = 10U;
    result.command_10_packet_0[1] = command_10_word_0;
    result.command_10_packet_0[2] = command_10_word_1;
    result.command_10_packet_1[0] = 10U;
    result.command_10_packet_1[1] = state_51c948;
    result.command_10_packet_1[2] = command_10_word_2;
    result.state_51c940 = first_response;
    result.state_51c944 = second_response;
    result.state_51c94c = computed_state_51c94c;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.command_10 = 10U;
    result.record_zero_path = record_30 == 0U ? 1U : 0U;
    result.continuation = record_30 == 0U ? 0x0008ccf0U : 0x0008d094U;
    return result;
}
