/* Selector-4 packet/state prefix recovered from i960 0x89930-0x899d8. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 record_184;
    recovered_u32 record_8;
    recovered_u32 record_10;
    recovered_u32 first_fifo_response;
    recovered_u32 second_fifo_response;
    recovered_u32 stored_record_184_plus_6000;
    recovered_u32 packet_record_184_plus_6000_low16;
    recovered_u32 derived_first_word;
    recovered_u32 derived_difference;
    recovered_u32 packet_29[3];
    recovered_u32 packet_30[3];
    recovered_u32 state_51c940;
    recovered_u32 state_51c948;
    recovered_u32 state_51c950;
    recovered_u32 state_51c954;
    recovered_u32 timing_minus_3;
    recovered_u32 fifo_address;
    recovered_u32 float_constant;
    recovered_u32 first_command;
    recovered_u32 second_command;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_89930_packet_state_prefix_result;

recovered_startup_mode4_arm_89930_packet_state_prefix_result
recovered_startup_mode4_arm_89930_packet_state_prefix(
    recovered_u32 record_184, recovered_u32 record_8, recovered_u32 record_10,
    recovered_u32 first_fifo_response, recovered_u32 second_fifo_response,
    recovered_u32 timing)
{
    recovered_startup_mode4_arm_89930_packet_state_prefix_result result;

    result.record_184 = record_184;
    result.record_8 = record_8;
    result.record_10 = record_10;
    result.first_fifo_response = first_fifo_response;
    result.second_fifo_response = second_fifo_response;
    result.stored_record_184_plus_6000 = record_184 + 0x6000U;
    result.packet_record_184_plus_6000_low16 =
        result.stored_record_184_plus_6000 & 0xffffU;
    result.derived_first_word = first_fifo_response + record_8;
    result.derived_difference = record_10 - second_fifo_response;
    result.packet_29[0] = 29U;
    result.packet_29[1] = result.packet_record_184_plus_6000_low16;
    result.packet_29[2] = 0x42a00000U;
    result.packet_30[0] = 30U;
    result.packet_30[1] = result.packet_record_184_plus_6000_low16;
    result.packet_30[2] = 0x42a00000U;
    result.state_51c940 = result.stored_record_184_plus_6000;
    result.state_51c948 = 0x42a00000U;
    result.state_51c950 = result.derived_first_word;
    result.state_51c954 = result.derived_difference;
    result.timing_minus_3 = timing - 3U;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.float_constant = 0x42a00000U;
    result.first_command = 29U;
    result.second_command = 30U;
    result.continuation = 0x000899d8U;
    return result;
}
