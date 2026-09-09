/* Selector-0 packet/state prefix recovered from i960 0x8b754-0x8b7e0. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 first_response;
    recovered_u32 transformed_base;
    recovered_u32 masked_operand;
    recovered_u32 packet_float_word;
    recovered_u32 second_response;
    recovered_u32 current_record_8;
    recovered_u32 current_record_10;
    recovered_u32 command_29_packet[3];
    recovered_u32 command_30_packet[3];
    recovered_u32 state_51c940;
    recovered_u32 state_51c948;
    recovered_u32 state_51c950;
    recovered_u32 state_51c954;
    recovered_u32 fifo_address;
    recovered_u32 command_29;
    recovered_u32 command_30;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8b754_packet_state_prefix_result;

recovered_startup_mode4_arm_8b754_packet_state_prefix_result
recovered_startup_mode4_arm_8b754_packet_state_prefix(
    recovered_u32 first_response, recovered_u32 second_response,
    recovered_u32 current_record_8, recovered_u32 current_record_10)
{
    recovered_startup_mode4_arm_8b754_packet_state_prefix_result result;

    result.first_response = first_response;
    result.transformed_base = first_response + 0x1000U;
    result.masked_operand = result.transformed_base & 0xffffU;
    result.packet_float_word = 0x42200000U;
    result.second_response = second_response;
    result.current_record_8 = current_record_8;
    result.current_record_10 = current_record_10;
    result.command_29_packet[0] = 29U;
    result.command_29_packet[1] = result.masked_operand;
    result.command_29_packet[2] = result.packet_float_word;
    result.command_30_packet[0] = 30U;
    result.command_30_packet[1] = result.masked_operand;
    result.command_30_packet[2] = result.packet_float_word;
    result.state_51c940 = result.transformed_base;
    result.state_51c948 = result.packet_float_word;
    result.state_51c950 = second_response + current_record_8;
    result.state_51c954 = current_record_10 - second_response;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.command_29 = 29U;
    result.command_30 = 30U;
    result.continuation = 0x0008b7e0U;
    return result;
}
