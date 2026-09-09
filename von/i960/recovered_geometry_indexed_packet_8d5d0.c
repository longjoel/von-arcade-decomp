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
    /* Object +0x4 index loaded into g4 before the bound comparison. */
    recovered_u32 object_index;
    /* Incoming g2 bound used by cmpibg/subo before the table lookup. */
    recovered_u32 index_bound;
    recovered_u32 row_scale;
};

struct recovered_geometry_indexed_packet_8d5d0_plan {
    recovered_u32 fifo_word[10];
    recovered_u32 fifo_count;
    recovered_u32 xor_mask;
    recovered_u32 normalized_count;
    recovered_u32 next_record_offset;
    recovered_u32 extended_records_enabled;
    recovered_u32 adjusted_index;
    recovered_u32 table_byte_offset;
    recovered_u32 extended_record_count;
    recovered_u32 extended_record_stride;
    recovered_u32 extended_source_start_offset;
    recovered_u32 extended_destination_start_offset;
};

static recovered_u32 recovered_sign_extend_halfword(recovered_u32 value)
{
    return (recovered_u32)(int32_t)(int16_t)(value & 0xffffU);
}

static recovered_u32 recovered_negate_signed_halfword(recovered_u32 value)
{
    return (recovered_u32)(0 - recovered_sign_extend_halfword(value));
}

void recovered_geometry_indexed_packet_8d5d0(
    const struct recovered_geometry_indexed_packet_8d5d0_input *input,
    struct recovered_geometry_indexed_packet_8d5d0_plan *plan)
{
    int index = (int)(int16_t)(input->object_index & 0xffffU);
    int row_scale = (int)(int16_t)(input->row_scale & 0xffffU);
    int count = (int)(int16_t)(input->signed_count & 0xffffU);
    int32_t index_bound = (int32_t)input->index_bound;
    int normalized = count < 0 ? -count : count;
    recovered_u32 normalized_bits = (recovered_u32)normalized;
    recovered_u32 adjusted_index = (recovered_u32)(index > index_bound ?
        index_bound : index - 1);
    recovered_u32 mask = 0x8000U;
    plan->fifo_word[0] = 20U;
    plan->fifo_word[1] = recovered_negate_signed_halfword(input->value_0);
    plan->fifo_word[2] = 21U;
    plan->fifo_word[3] = recovered_negate_signed_halfword(input->value_2);
    plan->fifo_word[4] = 22U;
    plan->fifo_word[5] = recovered_negate_signed_halfword(input->value_4);
    plan->fifo_word[6] = 47U;
    /* 0x8d6b4/0x8d6a4/0x8d6b4 use ldos values directly for the XOR. */
    plan->fifo_word[7] = recovered_sign_extend_halfword(input->value_6) ^ mask;
    plan->fifo_word[8] = recovered_sign_extend_halfword(input->value_8) ^ mask;
    plan->fifo_word[9] = recovered_sign_extend_halfword(input->value_10) ^ mask;
    plan->fifo_count = 10U;
    plan->xor_mask = mask;
    plan->normalized_count = normalized_bits;
    plan->next_record_offset = 12U;
    /* The ble at 0x8d6e8 skips the later indexed-record loop for values
     * through one; the ten-word prefix above has already been emitted. */
    plan->extended_records_enabled = normalized > 1 ? 1U : 0U;
    plan->adjusted_index = adjusted_index;
    plan->table_byte_offset = adjusted_index * (recovered_u32)row_scale * 12U;
    plan->extended_record_count = normalized > 1 ? normalized_bits - 1U : 0U;
    plan->extended_record_stride = 12U;
    plan->extended_source_start_offset = plan->extended_record_count ? 12U : 0U;
    plan->extended_destination_start_offset = plan->extended_record_count ?
        normalized_bits * 12U : 0U;
}
