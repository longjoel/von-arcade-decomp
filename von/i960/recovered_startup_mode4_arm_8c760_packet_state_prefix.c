/* Selector-3 packet/state prefix recovered from i960 0x8c760-0x8c7f0. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 record_184;
    recovered_u32 transformed_base;
    recovered_u32 masked_operand;
    recovered_u32 second_response;
    recovered_u32 current_record_8;
    recovered_u32 current_record_10;
    recovered_u32 packet_float_word;
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
} recovered_startup_mode4_arm_8c760_packet_state_prefix_result;

recovered_startup_mode4_arm_8c760_packet_state_prefix_result
recovered_startup_mode4_arm_8c760_packet_state_prefix(
    recovered_u32 record_184, recovered_u32 second_response,
    recovered_u32 current_record_8, recovered_u32 current_record_10)
{
    recovered_startup_mode4_arm_8c760_packet_state_prefix_result result;

    result.record_184 = record_184;
    result.transformed_base = record_184 + 0x6000U;
    result.masked_operand = result.transformed_base & 0xffffU;
    result.second_response = second_response;
    result.current_record_8 = current_record_8;
    result.current_record_10 = current_record_10;
    result.packet_float_word = 0x42a00000U;
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
    result.continuation = 0x0008c7f0U;
    return result;
}
