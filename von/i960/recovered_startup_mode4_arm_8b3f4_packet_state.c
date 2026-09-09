/* Selector-3 packet/state builder recovered from i960 0x8b3f4-0x8b4e8. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 state_51c940;
    recovered_u32 state_51c948;
    recovered_u32 counter_51c984;
    recovered_u32 command_29_packet[3];
    recovered_u32 command_30_packet[3];
    recovered_u32 first_response;
    recovered_u32 second_response;
    recovered_u32 current_record_8;
    recovered_u32 current_record_10;
    recovered_u32 linked_record_8;
    recovered_u32 linked_record_10;
    recovered_u32 rolling_51c958;
    recovered_u32 rolling_51c95c;
    recovered_u32 rolling_51c960;
    recovered_u32 state_51c94c;
    recovered_u32 command_10;
    recovered_u32 fifo_address;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8b3f4_packet_state_result;

recovered_startup_mode4_arm_8b3f4_packet_state_result
recovered_startup_mode4_arm_8b3f4_packet_state(
    recovered_u32 state_51c940, recovered_u32 state_51c948,
    recovered_u32 counter_51c984, recovered_u32 first_response,
    recovered_u32 second_response, recovered_u32 current_record_8,
    recovered_u32 current_record_10, recovered_u32 linked_record_8,
    recovered_u32 linked_record_10, recovered_u32 rolling_51c958,
    recovered_u32 rolling_51c95c, recovered_u32 rolling_51c960,
    recovered_u32 state_51c94c)
{
    recovered_startup_mode4_arm_8b3f4_packet_state_result result;

    result.state_51c940 = state_51c940;
    result.state_51c948 = state_51c948;
    result.counter_51c984 = counter_51c984;
    result.command_29_packet[0] = 29U;
    result.command_29_packet[1] = state_51c940 & 0xffffU;
    result.command_29_packet[2] = state_51c948;
    result.command_30_packet[0] = 30U;
    result.command_30_packet[1] = state_51c940 & 0xffffU;
    result.command_30_packet[2] = state_51c948;
    result.first_response = first_response;
    result.second_response = second_response;
    result.current_record_8 = current_record_8;
    result.current_record_10 = current_record_10;
    result.linked_record_8 = linked_record_8;
    result.linked_record_10 = linked_record_10;
    result.rolling_51c958 = rolling_51c958;
    result.rolling_51c95c = rolling_51c95c;
    result.rolling_51c960 = rolling_51c960;
    result.state_51c94c = state_51c94c;
    result.command_10 = 10U;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.continuation = 0x0008b4e8U;
    return result;
}
