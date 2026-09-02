/* Data-table contract for the records embedded at i960 0x1f680. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_status_code_table_plan {
    u32 base;
    u32 record_count;
    u32 record_size;
    u32 blank_record_index;
    u32 text_position_column;
    u32 text_position_row;
};

u32 recovered_status_code_record_address(u32 index)
{
    if (index >= 9U)
        return 0U;
    return 0x0001f680U + (index << 4);
}

void recovered_status_code_table_plan(struct recovered_status_code_table_plan *plan)
{
    plan->base = 0x0001f680U;
    plan->record_count = 9U;
    plan->record_size = 16U;
    plan->blank_record_index = 8U;
    plan->text_position_column = 8U;
    plan->text_position_row = 14U;
}
