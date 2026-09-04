/* Pure indexed geometry packet prefix recovered from i960 0x8d5d0-0x8d6b8. */
#include "recovered_common.h"

struct recovered_geometry_indexed_packet_8d5d0_input {
    recovered_u32 value_0;
    recovered_u32 value_2;
    recovered_u32 value_4;
    recovered_u32 value_6;
    recovered_u32 value_8;
    recovered_u32 value_10;
    recovered_u32 signed_count;
};

struct recovered_geometry_indexed_packet_8d5d0_plan {
    recovered_u32 fifo_word[10];
    recovered_u32 fifo_count;
    recovered_u32 xor_mask;
    recovered_u32 normalized_count;
    recovered_u32 next_record_offset;
};

void recovered_geometry_indexed_packet_8d5d0(
    const struct recovered_geometry_indexed_packet_8d5d0_input *input,
    struct recovered_geometry_indexed_packet_8d5d0_plan *plan)
{
    recovered_u32 count = input->signed_count & 0xffffU;
    recovered_u32 mask = (count == 1U) ? 0x8000U : 0U;
    plan->fifo_word[0] = 20U;
    plan->fifo_word[1] = (0U - (input->value_0 & 0xffffU)) & 0xffffU;
    plan->fifo_word[2] = 21U;
    plan->fifo_word[3] = (0U - (input->value_2 & 0xffffU)) & 0xffffU;
    plan->fifo_word[4] = 22U;
    plan->fifo_word[5] = (0U - (input->value_4 & 0xffffU)) & 0xffffU;
    plan->fifo_word[6] = 47U;
    plan->fifo_word[7] = (input->value_6 & 0xffffU) ^ mask;
    plan->fifo_word[8] = (input->value_8 & 0xffffU) ^ mask;
    plan->fifo_word[9] = (input->value_10 & 0xffffU) ^ mask;
    plan->fifo_count = 10U;
    plan->xor_mask = mask;
    plan->normalized_count = count;
    plan->next_record_offset = 12U;
}
