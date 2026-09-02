/* Signed status-value route recovered from i960 0x1fbe0/0x1e7c0. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_status_value_route {
    RECOVERED_STATUS_VALUE_BLOCK_AND_GLYPH = 0,
    RECOVERED_STATUS_VALUE_CLEAR = 1,
};

struct recovered_status_value_plan {
    u32 route;
    u32 block_helper;
    u32 block_source;
    u32 block_width;
    u32 block_height;
    u32 block_uses_current_position;
    u32 column_advance;
    u32 glyph_helper;
    u32 glyph_source_table;
    u32 glyph_index;
    u32 glyph_width;
    u32 glyph_height;
    u32 clear_helper;
    u32 clear_width;
    u32 clear_height;
};

void recovered_status_value_plan(int32_t value,
                                 struct recovered_status_value_plan *plan)
{
    plan->block_helper = 0U;
    plan->block_source = 0U;
    plan->block_width = 0U;
    plan->block_height = 0U;
    plan->block_uses_current_position = 0U;
    plan->column_advance = 0U;
    plan->glyph_helper = 0U;
    plan->glyph_source_table = 0U;
    plan->glyph_index = 0U;
    plan->glyph_width = 0U;
    plan->glyph_height = 0U;
    plan->clear_helper = 0U;
    plan->clear_width = 0U;
    plan->clear_height = 0U;

    if (value < 0) {
        plan->route = RECOVERED_STATUS_VALUE_BLOCK_AND_GLYPH;
        plan->block_helper = 0x0001dc10U;
        plan->block_source = 0x02fe17ecU;
        plan->block_width = 20U;
        plan->block_height = 3U;
        plan->block_uses_current_position = 1U;
        plan->column_advance = 21U;
        plan->glyph_helper = 0x0001dc10U;
        plan->glyph_source_table = 0x02ea1fd0U;
        plan->glyph_index = ((u32)value - 0x30U) & 15U;
        plan->glyph_width = 4U;
        plan->glyph_height = 3U;
    } else {
        plan->route = RECOVERED_STATUS_VALUE_CLEAR;
        plan->clear_helper = 0x0001df00U;
        plan->clear_width = 25U;
        plan->clear_height = 3U;
    }
}
