/* Deterministic packet/control contract for i960 0x8d850-0x8da54. */
#include "recovered_common.h"

struct recovered_geometry_indexed_batch_8d850_input {
    recovered_u32 source_m2, source_0, source_2, source_4, source_6;
    recovered_u32 selected_value_0;
    recovered_u32 record_word, record_word_4, record_word_8;
    recovered_u32 signed_count, object_index, index_bound;
    recovered_u32 readback_word;
    recovered_u32 record_active_word, table_index;
    recovered_u32 selected_record_dword, selected_record_word_8;
    recovered_u32 row_scale;
};

struct recovered_geometry_indexed_batch_8d850_plan {
    recovered_u32 fifo_word[13], fifo_count;
    recovered_u32 packet_emitted, normalized_count, adjusted_index, table_byte_offset;
    recovered_u32 window_word[4], window_address[4];
    recovered_u32 control_address, control_value, completion_word;
    recovered_u32 extended_record_count, extended_record_stride;
    recovered_u32 source_start_offset, destination_start_offset;
    recovered_u32 table_write, table_address, table_low_value, table_high_value;
};

static recovered_u32 sign_extend_halfword(recovered_u32 value)
{
    return (recovered_u32)(int32_t)(int16_t)(value & 0xffffU);
}

void recovered_geometry_indexed_batch_8d850(
    const struct recovered_geometry_indexed_batch_8d850_input *input,
    struct recovered_geometry_indexed_batch_8d850_plan *plan)
{
    int index = (int)(int16_t)(input->object_index & 0xffffU);
    int32_t bound = (int32_t)input->index_bound;
    int row_scale = (int)(int16_t)(input->row_scale & 0xffffU);
    int count = (int)(int16_t)(input->signed_count & 0xffffU);
    int normalized = count < 0 ? -count : count;
    recovered_u32 adjusted_index = (recovered_u32)(index > bound ? bound : index - 1);

    plan->fifo_word[0] = 5U;
    plan->fifo_word[1] = 47U;
    plan->fifo_word[2] = input->source_m2 & 0xffffU;
    plan->fifo_word[3] = input->source_0 & 0xffffU;
    plan->fifo_word[4] = input->source_2 & 0xffffU;
    plan->fifo_word[5] = 22U;
    plan->fifo_word[6] = input->source_4 & 0xffffU;
    plan->fifo_word[7] = 21U;
    plan->fifo_word[8] = input->source_6 & 0xffffU;
    plan->fifo_word[9] = 20U;
    plan->fifo_word[10] = sign_extend_halfword(input->selected_value_0);
    plan->fifo_word[11] = 58U;
    plan->fifo_word[12] = input->readback_word;
    plan->fifo_count = 13U;
    plan->normalized_count = (recovered_u32)normalized;
    plan->packet_emitted = normalized > 0 ? 1U : 0U;
    plan->adjusted_index = adjusted_index;
    plan->table_byte_offset = adjusted_index * (recovered_u32)row_scale * 12U;
    plan->window_address[0] = 0x804000U;
    plan->window_address[1] = 0x804004U;
    plan->window_address[2] = 0x804008U;
    plan->window_address[3] = 0x80400cU;
    plan->window_word[0] = input->record_word;
    plan->window_word[1] = input->record_word_4;
    plan->window_word[2] = input->record_word_8;
    plan->window_word[3] = 0U;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->completion_word = 6U;
    plan->extended_record_count = (recovered_u32)normalized;
    plan->extended_record_stride = 12U;
    plan->source_start_offset = 0U;
    plan->destination_start_offset = 0U;
    plan->table_write = input->record_active_word == 0U && input->table_index <= 5U;
    plan->table_address = 0x562430U + input->table_index * 12U;
    plan->table_low_value = input->selected_record_dword;
    plan->table_high_value = input->selected_record_word_8;
}
