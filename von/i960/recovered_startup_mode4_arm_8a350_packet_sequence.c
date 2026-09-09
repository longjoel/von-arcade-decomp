/* Selector-2 packet sequence recovered from i960 0x8a350-0x8a43c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 state_51c940;
    recovered_u32 state_51c948;
    recovered_u32 record_8;
    recovered_u32 record_10;
    recovered_u32 linked_record_8;
    recovered_u32 linked_record_10;
    recovered_u32 command_29_response;
    recovered_u32 command_30_response;
    recovered_u32 command_10_response;
    recovered_u32 command_29_packet[3];
    recovered_u32 command_30_packet[3];
    recovered_u32 command_10_packet[3];
    recovered_u32 command_31_packet[7];
    recovered_u32 command_29_operand;
    recovered_u32 command_31_first_word;
    recovered_u32 command_31_fifth_word;
    recovered_u32 fifo_address;
    recovered_u32 first_command;
    recovered_u32 second_command;
    recovered_u32 third_command;
    recovered_u32 fourth_command;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8a350_packet_sequence_result;

recovered_startup_mode4_arm_8a350_packet_sequence_result
recovered_startup_mode4_arm_8a350_packet_sequence(
    recovered_u32 state_51c940, recovered_u32 state_51c948,
    recovered_u32 record_8, recovered_u32 record_10,
    recovered_u32 linked_record_8, recovered_u32 linked_record_10,
    recovered_u32 command_29_response, recovered_u32 command_30_response,
    recovered_u32 command_10_response)
{
    recovered_startup_mode4_arm_8a350_packet_sequence_result result;
    recovered_u32 command_29_plus_record_8;
    recovered_u32 record_10_minus_command_30;

    result.state_51c940 = state_51c940;
    result.state_51c948 = state_51c948;
    result.record_8 = record_8;
    result.record_10 = record_10;
    result.linked_record_8 = linked_record_8;
    result.linked_record_10 = linked_record_10;
    result.command_29_response = command_29_response;
    result.command_30_response = command_30_response;
    result.command_10_response = command_10_response;
    result.command_29_operand = state_51c940 & 0xffffU;
    result.command_29_packet[0] = 29U;
    result.command_29_packet[1] = result.command_29_operand;
    result.command_29_packet[2] = state_51c948;
    result.command_30_packet[0] = 30U;
    result.command_30_packet[1] = result.command_29_operand;
    result.command_30_packet[2] = state_51c948;
    command_29_plus_record_8 = command_29_response + record_8;
    record_10_minus_command_30 = record_10 - command_30_response;
    result.command_10_packet[0] = 10U;
    result.command_10_packet[1] = linked_record_10 - record_10_minus_command_30;
    result.command_10_packet[2] = command_29_plus_record_8 - linked_record_8;
    result.command_31_packet[0] = 31U;
    result.command_31_packet[1] = command_29_plus_record_8;
    result.command_31_packet[2] = linked_record_8;
    result.command_31_packet[3] = 0U;
    result.command_31_packet[4] = 0U;
    result.command_31_packet[5] = record_10_minus_command_30;
    result.command_31_packet[6] = linked_record_10;
    result.command_31_first_word = command_29_plus_record_8;
    result.command_31_fifth_word = record_10_minus_command_30;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.first_command = 29U;
    result.second_command = 30U;
    result.third_command = 10U;
    result.fourth_command = 31U;
    result.continuation = 0x0008a43cU;
    return result;
}
