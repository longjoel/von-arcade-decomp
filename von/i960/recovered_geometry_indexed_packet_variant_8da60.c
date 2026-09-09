/* Deterministic prefix/control contract for i960 0x8da60-0x8dd30. */
#include "recovered_common.h"

struct recovered_geometry_indexed_packet_variant_8da60_input {
    recovered_u32 value_0, value_2, value_4;
    recovered_u32 value_6, value_8, value_10;
    recovered_u32 record_dword_0, record_word_8;
    recovered_u32 signed_count;
    recovered_u32 object_index, index_bound;
    recovered_u32 row_scale;
};

struct recovered_geometry_indexed_packet_variant_8da60_plan {
    recovered_u32 fifo_word[10], fifo_count, packet_emitted, xor_mask;
    recovered_u32 normalized_count, adjusted_index, table_byte_offset;
    recovered_u32 published_low, published_high;
    recovered_u32 extended_record_count, extended_record_stride;
    recovered_u32 extended_source_start_offset;
    recovered_u32 extended_destination_start_offset;
};

static recovered_u32 sign_extend_halfword(recovered_u32 value)
{
    return (recovered_u32)(int32_t)(int16_t)(value & 0xffffU);
}

void recovered_geometry_indexed_packet_variant_8da60(
    const struct recovered_geometry_indexed_packet_variant_8da60_input *input,
    struct recovered_geometry_indexed_packet_variant_8da60_plan *plan)
{
    int index = (int)(int16_t)(input->object_index & 0xffffU);
    int32_t bound = (int32_t)input->index_bound;
    int row_scale = (int)(int16_t)(input->row_scale & 0xffffU);
    int count = (int)(int16_t)(input->signed_count & 0xffffU);
    int normalized = count < 0 ? -count : count;
    recovered_u32 adjusted_index = (recovered_u32)(index > bound ? bound : index - 1);
    recovered_u32 mask = 0x8000U;

    plan->fifo_word[0] = 20U;
    plan->fifo_word[1] = (recovered_u32)(0 - sign_extend_halfword(input->value_0));
    plan->fifo_word[2] = 21U;
    plan->fifo_word[3] = (recovered_u32)(0 - sign_extend_halfword(input->value_2));
    plan->fifo_word[4] = 22U;
    plan->fifo_word[5] = (recovered_u32)(0 - sign_extend_halfword(input->value_4));
    plan->fifo_word[6] = 58U;
    plan->fifo_word[7] = sign_extend_halfword(input->value_6) ^ mask;
    plan->fifo_word[8] = sign_extend_halfword(input->value_8) ^ mask;
    plan->fifo_word[9] = sign_extend_halfword(input->value_10) ^ mask;
    plan->fifo_count = 10U;
    plan->packet_emitted = normalized > 0 ? 1U : 0U;
    plan->xor_mask = mask;
    plan->normalized_count = (recovered_u32)normalized;
    plan->adjusted_index = adjusted_index;
    plan->table_byte_offset = adjusted_index * (recovered_u32)row_scale * 12U;
    plan->published_low = input->record_dword_0;
    plan->published_high = input->record_word_8;
    plan->extended_record_count = normalized > 1 ? (recovered_u32)normalized - 1U : 0U;
    plan->extended_record_stride = 12U;
    plan->extended_source_start_offset = plan->extended_record_count ? 12U : 0U;
    plan->extended_destination_start_offset = plan->extended_record_count ?
        (recovered_u32)normalized * 12U : 0U;
}
