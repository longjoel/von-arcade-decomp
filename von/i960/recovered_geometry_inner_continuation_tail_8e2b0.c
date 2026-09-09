/* Continuation-loop tail from i960 0x8e2b0-0x8e300. */
#include "recovered_common.h"

struct recovered_geometry_inner_continuation_tail_8e2b0_input {
    recovered_u32 table_arm_active;
    recovered_u32 table_index;
    recovered_u32 selected_record_dword;
    recovered_u32 selected_record_word_8;
    recovered_u32 table_cursor;
    recovered_u32 auxiliary_cursor;
    recovered_u32 source_cursor;
    recovered_u32 destination_cursor;
    recovered_u32 record_counter;
    recovered_u32 object_cursor;
    recovered_u32 destination_record_cursor;
    recovered_u32 record_limit;
};

struct recovered_geometry_inner_continuation_tail_8e2b0_plan {
    recovered_u32 table_write;
    recovered_u32 table_address;
    recovered_u32 table_low_value;
    recovered_u32 table_high_value;
    recovered_u32 next_table_cursor;
    recovered_u32 next_auxiliary_cursor;
    recovered_u32 next_source_cursor;
    recovered_u32 next_destination_cursor;
    recovered_u32 next_record_counter;
    recovered_u32 next_object_cursor;
    recovered_u32 next_destination_record_cursor;
    recovered_u32 continuation_taken;
    recovered_u32 continuation_entry;
};

void recovered_geometry_inner_continuation_tail_8e2b0(
    const struct recovered_geometry_inner_continuation_tail_8e2b0_input *input,
    struct recovered_geometry_inner_continuation_tail_8e2b0_plan *plan)
{
    plan->table_write = input->table_arm_active && input->table_index <= 5U;
    plan->table_address = 0x562430U + input->table_index * 12U;
    plan->table_low_value = input->selected_record_dword;
    plan->table_high_value = input->selected_record_word_8;
    plan->next_table_cursor = input->table_cursor + 12U;
    plan->next_auxiliary_cursor = input->auxiliary_cursor + 2U;
    plan->next_source_cursor = input->source_cursor + 12U;
    plan->next_destination_cursor = input->destination_cursor + 12U;
    plan->next_record_counter = input->record_counter + 1U;
    plan->next_object_cursor = input->object_cursor + 8U;
    plan->next_destination_record_cursor = input->destination_record_cursor + 12U;
    plan->continuation_taken = input->record_counter < input->record_limit ? 1U : 0U;
    plan->continuation_entry = 0x8e120U;
}
