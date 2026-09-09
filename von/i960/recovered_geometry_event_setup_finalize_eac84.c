/* Event setup-helper terminal packet tail recovered from i960 0xeac84-ead1c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 workspace_word_10_sum;
    recovered_u32 fifo_response_opcode_30;
    recovered_u32 fifo_response_opcode_10;
    recovered_u32 division_result_g6;
    recovered_u32 state_word_g2;
    recovered_u32 first_packet_response_r4;
    recovered_u32 packet_20[2];
    recovered_u32 packet_21[2];
    recovered_u32 packet_18[4];
    recovered_u32 packet_20_count;
    recovered_u32 packet_21_count;
    recovered_u32 packet_18_count;
    recovered_u32 masked_fifo_word;
    recovered_u32 negative_state_address;
    recovered_u32 state_3f8;
    recovered_u32 state_3f8_address;
    recovered_u32 fifo_address;
    recovered_u32 opcode_20;
    recovered_u32 opcode_21;
    recovered_u32 opcode_18;
    recovered_u32 next_target;
} recovered_geometry_event_setup_finalize_result_eac84;

recovered_geometry_event_setup_finalize_result_eac84
recovered_geometry_event_setup_finalize_eac84(
    recovered_u32 workspace_word_10_sum, recovered_u32 fifo_response_opcode_30,
    recovered_u32 fifo_response_opcode_10, recovered_u32 division_result_g6,
    recovered_u32 state_word_g2,
    recovered_u32 first_packet_response_r4)
{
    recovered_geometry_event_setup_finalize_result_eac84 result;

    result.workspace_word_10_sum = workspace_word_10_sum;
    result.fifo_response_opcode_30 = fifo_response_opcode_30;
    result.fifo_response_opcode_10 = fifo_response_opcode_10;
    result.division_result_g6 = division_result_g6;
    result.state_word_g2 = state_word_g2;
    result.first_packet_response_r4 = first_packet_response_r4;
    result.masked_fifo_word = fifo_response_opcode_10 & 0xffffU;
    result.negative_state_address = 0U - 0x005783e4U;

    result.packet_20[0] = 20U;
    result.packet_20[1] = result.masked_fifo_word;
    result.packet_21[0] = 21U;
    result.packet_21[1] = result.negative_state_address;
    result.packet_18[0] = 18U;
    result.packet_18[1] = state_word_g2 ^ 0x80000000U;
    result.packet_18[2] = first_packet_response_r4 ^ 0x80000000U;
    result.packet_18[3] = division_result_g6 ^ 0x80000000U;
    result.packet_20_count = 2U;
    result.packet_21_count = 2U;
    result.packet_18_count = 4U;
    result.state_3f8 = division_result_g6;
    result.state_3f8_address = 0x005783f8U;
    result.fifo_address = RECOVERED_FIFO_ADDRESS;
    result.opcode_20 = 20U;
    result.opcode_21 = 21U;
    result.opcode_18 = 18U;
    result.next_target = 0x000ead1cU;
    return result;
}
