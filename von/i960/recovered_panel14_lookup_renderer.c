/* Masked lookup renderer recovered from i960 0x1ff50. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_panel14_lookup_plan {
    u32 helper;
    u32 source_table;
    u32 source;
    u32 table_index;
    u32 width;
    u32 height;
    u32 column_advance;
    u32 max_column;
};

void recovered_panel14_lookup_plan(u32 value, u32 current_column, u32 caller_g30,
                                   struct recovered_panel14_lookup_plan *plan)
{
    plan->helper = 0x0001dc10U;
    plan->source_table = 0x02ea2090U;
    plan->table_index = (value - 48U) & 15U;
    plan->source = plan->source_table + plan->table_index * 4U;
    plan->width = 1U;
    plan->height = 2U;
    plan->max_column = caller_g30 + 31U;
    plan->column_advance = current_column <= plan->max_column ? 1U : 0U;
}
