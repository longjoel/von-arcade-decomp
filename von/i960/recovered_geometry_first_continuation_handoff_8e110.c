/* Cursor handoff from the first-record arm into i960 0x8e120. */
#include "recovered_common.h"

struct recovered_geometry_first_continuation_handoff_8e110_input {
    recovered_u32 table_cursor;
    recovered_u32 auxiliary_cursor;
    recovered_u32 source_cursor;
    recovered_u32 destination_cursor;
};

struct recovered_geometry_first_continuation_handoff_8e110_plan {
    recovered_u32 next_table_cursor;
    recovered_u32 next_auxiliary_cursor;
    recovered_u32 next_source_cursor;
    recovered_u32 next_destination_cursor;
    recovered_u32 continuation_entry;
};

void recovered_geometry_first_continuation_handoff_8e110(
    const struct recovered_geometry_first_continuation_handoff_8e110_input *input,
    struct recovered_geometry_first_continuation_handoff_8e110_plan *plan)
{
    plan->next_table_cursor = input->table_cursor + 12U;
    plan->next_auxiliary_cursor = input->auxiliary_cursor + 2U;
    plan->next_source_cursor = input->source_cursor + 8U;
    plan->next_destination_cursor = input->destination_cursor + 8U;
    plan->continuation_entry = 0x8e120U;
}
