/* Selector-1 packet prefix recovered from i960 0x8b944-0x8b9e4. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 first_response;
    recovered_u32 transformed_base;
    recovered_u32 masked_operand;
    recovered_u32 followup_masked_operand;
    recovered_u32 packet_float_word;
    recovered_u32 command_29_packet[3];
    recovered_u32 command_30_packet[3];
    recovered_u32 followup_packet[3];
    recovered_u32 fifo_address;
    recovered_u32 command_29;
    recovered_u32 command_30;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8b944_packet_prefix_result;

recovered_startup_mode4_arm_8b944_packet_prefix_result
recovered_startup_mode4_arm_8b944_packet_prefix(recovered_u32 first_response)
{
    recovered_startup_mode4_arm_8b944_packet_prefix_result result;

    result.first_response = first_response;
    result.transformed_base = first_response + 0x1000U;
    result.masked_operand = result.transformed_base & 0xffffU;
    result.followup_masked_operand = (first_response + 0x5000U) & 0xffffU;
    result.packet_float_word = 0x42200000U;
    result.command_29_packet[0] = 29U;
    result.command_29_packet[1] = result.masked_operand;
    result.command_29_packet[2] = result.packet_float_word;
    result.command_30_packet[0] = 30U;
    result.command_30_packet[1] = result.masked_operand;
    result.command_30_packet[2] = result.packet_float_word;
    result.followup_packet[0] = result.transformed_base;
    result.followup_packet[1] = result.followup_masked_operand;
    result.followup_packet[2] = result.packet_float_word;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.command_29 = 29U;
    result.command_30 = 30U;
    result.continuation = 0x0008b9e4U;
    return result;
}
