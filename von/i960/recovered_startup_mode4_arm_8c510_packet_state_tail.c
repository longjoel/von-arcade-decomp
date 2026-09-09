/* Selector-1 command/response tail recovered from i960 0x8c510-0x8c660. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 state_51c950;
    recovered_u32 rolling_51c958;
    recovered_u32 state_51c954;
    recovered_u32 rolling_51c960;
    recovered_u32 state_51c94c;
    recovered_u32 command_10_word_0;
    recovered_u32 command_10_word_1;
    recovered_u32 command_10_word_2;
    recovered_u32 command_10_word_3;
    recovered_u32 command_10_word_4;
    recovered_u32 first_response;
    recovered_u32 second_response;
    recovered_u32 marker_1d0;
    recovered_u32 record_30;
    recovered_u32 command_31_packet[6];
    recovered_u32 command_10_packet_0[3];
    recovered_u32 command_10_packet_1[3];
    recovered_u32 state_51c940;
    recovered_u32 state_51c944;
    recovered_u32 selector_51c99c;
    recovered_u32 state_51c9b4;
    recovered_u32 fifo_address;
    recovered_u32 command_31;
    recovered_u32 command_10;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8c510_packet_state_tail_result;

recovered_startup_mode4_arm_8c510_packet_state_tail_result
recovered_startup_mode4_arm_8c510_packet_state_tail(
    recovered_u32 state_51c950, recovered_u32 rolling_51c958,
    recovered_u32 state_51c954, recovered_u32 rolling_51c960,
    recovered_u32 state_51c94c, recovered_u32 command_10_word_0,
    recovered_u32 command_10_word_1, recovered_u32 command_10_word_2,
    recovered_u32 command_10_word_3, recovered_u32 command_10_word_4,
    recovered_u32 first_response, recovered_u32 second_response,
    recovered_u32 marker_1d0, recovered_u32 record_30)
{
    recovered_startup_mode4_arm_8c510_packet_state_tail_result result;

    result.state_51c950 = state_51c950;
    result.rolling_51c958 = rolling_51c958;
    result.state_51c954 = state_51c954;
    result.rolling_51c960 = rolling_51c960;
    result.state_51c94c = state_51c94c;
    result.command_10_word_0 = command_10_word_0;
    result.command_10_word_1 = command_10_word_1;
    result.command_10_word_2 = command_10_word_2;
    result.command_10_word_3 = command_10_word_3;
    result.command_10_word_4 = command_10_word_4;
    result.first_response = first_response;
    result.second_response = second_response;
    result.marker_1d0 = marker_1d0;
    result.record_30 = record_30;
    result.command_31_packet[0] = 31U;
    result.command_31_packet[1] = state_51c950;
    result.command_31_packet[2] = rolling_51c958;
    result.command_31_packet[3] = 0U;
    result.command_31_packet[4] = 0U;
    result.command_31_packet[5] = state_51c954;
    result.command_10_packet_0[0] = 10U;
    result.command_10_packet_0[1] = command_10_word_0;
    result.command_10_packet_0[2] = command_10_word_1;
    result.command_10_packet_1[0] = 10U;
    result.command_10_packet_1[1] = command_10_word_2;
    result.command_10_packet_1[2] = command_10_word_3;
    result.state_51c940 = first_response;
    result.state_51c944 = second_response;
    result.selector_51c99c = marker_1d0 == 0U ? 2U : 1U;
    result.state_51c9b4 = marker_1d0 != 0U && record_30 != 0U ? 1U : 0U;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.command_31 = 31U;
    result.command_10 = 10U;
    result.continuation = marker_1d0 == 0U ? 0x0008c90cU :
        (record_30 == 0U ? 0x0008c904U : 0x0008c90cU);
    return result;
}
