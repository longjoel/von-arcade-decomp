/* Selector-3 packet/state sequence recovered from i960 0x8a670-0x8a7e4. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 first_response;
    recovered_u32 state_51c948;
    recovered_u32 state_51c950;
    recovered_u32 state_51c954;
    recovered_u32 rolling_51c958;
    recovered_u32 rolling_51c95c;
    recovered_u32 rolling_51c960;
    recovered_u32 command_29_packet[3];
    recovered_u32 command_30_packet[3];
    recovered_u32 command_31_packet[5];
    recovered_u32 command_31_response;
    recovered_u32 state_51c940;
    recovered_u32 fifo_address;
    recovered_u32 command_10;
    recovered_u32 command_31;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8a670_packet_state_result;

recovered_startup_mode4_arm_8a670_packet_state_result
recovered_startup_mode4_arm_8a670_packet_state(
    recovered_u32 first_response, recovered_u32 state_51c940,
    recovered_u32 state_51c948, recovered_u32 state_51c954,
    recovered_u32 rolling_51c958, recovered_u32 rolling_51c95c,
    recovered_u32 rolling_51c960, recovered_u32 command_31_response)
{
    recovered_startup_mode4_arm_8a670_packet_state_result result;

    result.first_response = first_response;
    result.state_51c948 = state_51c948;
    result.state_51c950 = first_response;
    result.state_51c954 = state_51c954;
    result.rolling_51c958 = rolling_51c958;
    result.rolling_51c95c = rolling_51c95c;
    result.rolling_51c960 = rolling_51c960;
    result.command_29_packet[0] = 29U;
    result.command_29_packet[1] = state_51c940 & 0xffffU;
    result.command_29_packet[2] = state_51c948;
    result.command_30_packet[0] = 30U;
    result.command_30_packet[1] = state_51c940 & 0xffffU;
    result.command_30_packet[2] = state_51c948;
    result.command_31_packet[0] = 31U;
    result.command_31_packet[1] = rolling_51c958;
    result.command_31_packet[2] = rolling_51c95c;
    result.command_31_packet[3] = rolling_51c960;
    result.command_31_packet[4] = 0U;
    result.command_31_response = command_31_response;
    result.state_51c940 = command_31_response;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.command_10 = 10U;
    result.command_31 = 31U;
    result.continuation = 0x0008a7e4U;
    return result;
}
