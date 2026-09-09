/* Selector-0 post-dispatch prefix recovered from i960 0x8a964-0x8aa54. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 counter_51c984;
    recovered_u32 prior_response_base;
    recovered_u32 timing_delta;
    recovered_u32 packet_operand;
    recovered_u32 packet_float_word;
    recovered_u32 first_response;
    recovered_u32 second_response;
    recovered_u32 current_record_8;
    recovered_u32 current_record_10;
    recovered_u32 command_29_packet[3];
    recovered_u32 command_30_packet[3];
    recovered_u32 state_51c940;
    recovered_u32 state_51c942;
    recovered_u32 state_51c948;
    recovered_u32 state_51c950;
    recovered_u32 state_51c954;
    recovered_u32 fifo_address;
    recovered_u32 command_29;
    recovered_u32 command_30;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8a964_packet_state_prefix_result;

recovered_startup_mode4_arm_8a964_packet_state_prefix_result
recovered_startup_mode4_arm_8a964_packet_state_prefix(
    recovered_u32 counter_51c984, recovered_u32 prior_response_base,
    recovered_u32 packet_operand, recovered_u32 packet_float_word,
    recovered_u32 first_response, recovered_u32 second_response,
    recovered_u32 current_record_8, recovered_u32 current_record_10)
{
    recovered_startup_mode4_arm_8a964_packet_state_prefix_result result;

    result.counter_51c984 = counter_51c984;
    result.prior_response_base = prior_response_base;
    result.timing_delta = 0xb4U - counter_51c984;
    result.packet_operand = packet_operand;
    result.packet_float_word = packet_float_word;
    result.first_response = first_response;
    result.second_response = second_response;
    result.current_record_8 = current_record_8;
    result.current_record_10 = current_record_10;
    result.command_29_packet[0] = 29U;
    result.command_29_packet[1] = packet_operand & 0xffffU;
    result.command_29_packet[2] = packet_float_word;
    result.command_30_packet[0] = 30U;
    result.command_30_packet[1] = packet_operand & 0xffffU;
    result.command_30_packet[2] = packet_float_word;
    result.state_51c940 = packet_operand;
    result.state_51c942 = result.timing_delta << 8U;
    result.state_51c948 = packet_float_word;
    result.state_51c950 = first_response + current_record_8;
    result.state_51c954 = second_response - current_record_10;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.command_29 = 29U;
    result.command_30 = 30U;
    result.continuation = 0x0008aa54U;
    return result;
}
