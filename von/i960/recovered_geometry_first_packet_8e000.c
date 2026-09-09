/* First-record geometry packet prefix recovered from i960 0x8e000-0x8e110. */
#include "recovered_common.h"

struct recovered_geometry_first_packet_8e000_input {
    recovered_u32 value_0, value_2, value_4;
    recovered_u32 value_6, value_8, value_10;
    recovered_u32 table_pair_low, table_pair_high;
    recovered_u32 signed_count;
};

struct recovered_geometry_first_packet_8e000_plan {
    recovered_u32 fifo_word[11];
    recovered_u32 fifo_count;
    recovered_u32 xor_mask;
    recovered_u32 normalized_count;
    recovered_u32 object_field_24c;
    recovered_u32 extended_records_enabled;
    recovered_u32 next_record_stride;
    recovered_u32 continuation_record_count;
    recovered_u32 continuation_record_stride;
    recovered_u32 continuation_source_start_offset;
    recovered_u32 continuation_table_start_offset;
    recovered_u32 continuation_aux_start_offset;
    recovered_u32 continuation_destination_base_offset;
    recovered_u32 table_low_address, table_high_address;
    recovered_u32 table_pair_low, table_pair_high;
};

static recovered_u32 recovered_geometry_first_sign_extend(recovered_u32 value)
{
    return (recovered_u32)(int32_t)(int16_t)(value & 0xffffU);
}

void recovered_geometry_first_packet_8e000(
    const struct recovered_geometry_first_packet_8e000_input *input,
    struct recovered_geometry_first_packet_8e000_plan *plan)
{
    int32_t signed_count = (int32_t)(int16_t)(input->signed_count & 0xffffU);
    recovered_u32 value_0 = recovered_geometry_first_sign_extend(input->value_0);
    recovered_u32 value_2 = recovered_geometry_first_sign_extend(input->value_2);
    recovered_u32 value_4 = recovered_geometry_first_sign_extend(input->value_4);

    plan->fifo_word[0] = 20U;
    plan->fifo_word[1] = 0U - value_0;
    plan->fifo_word[2] = 21U;
    plan->fifo_word[3] = 0U - value_2;
    plan->fifo_word[4] = 22U;
    plan->fifo_word[5] = 0U - value_4;
    plan->fifo_word[6] = 46U; /* 31 + 15 */
    plan->fifo_word[7] = recovered_geometry_first_sign_extend(input->value_6) ^ 0x8000U;
    plan->fifo_word[8] = recovered_geometry_first_sign_extend(input->value_8) ^ 0x8000U;
    plan->fifo_word[9] = recovered_geometry_first_sign_extend(input->value_10) ^ 0x8000U;
    plan->fifo_word[10] = 58U; /* 31 + 27 */
    plan->fifo_count = 11U;
    plan->xor_mask = 0x8000U;
    plan->normalized_count = (recovered_u32)(signed_count < 0 ? -signed_count : signed_count);
    plan->object_field_24c = plan->normalized_count;
    plan->extended_records_enabled = plan->normalized_count > 1U ? 1U : 0U;
    plan->next_record_stride = 12U; /* addo r6,12,r6 at 0x8e100 */
    plan->continuation_record_count = plan->extended_records_enabled ?
        plan->normalized_count - 1U : 0U;
    plan->continuation_record_stride = 12U;
    plan->continuation_source_start_offset = plan->continuation_record_count ? 8U : 0U;
    plan->continuation_table_start_offset = plan->continuation_record_count ? 12U : 0U;
    plan->continuation_aux_start_offset = plan->continuation_record_count ? 2U : 0U;
    plan->continuation_destination_base_offset = plan->continuation_record_count ? 8U : 0U;
    plan->table_low_address = 0x562480U;
    plan->table_high_address = 0x562488U;
    plan->table_pair_low = input->table_pair_low;
    plan->table_pair_high = input->table_pair_high;
}
