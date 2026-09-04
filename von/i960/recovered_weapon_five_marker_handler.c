/* Handler contract recovered from i960 0x214bc-0x2157c. */
#include <stdint.h>
#include "recovered_common.h"

typedef uint32_t u32;

struct recovered_weapon_five_marker_plan {
    u32 text_helper;
    u32 text_plane;
    u32 text_column;
    u32 text_row;
    u32 text_width;
    u32 text_height;
    u32 marker_table_offset;
    u32 marker_start;
    u32 marker_value;
    u32 marker_count;
};

void recovered_weapon_five_marker_plan(u32 selector, u32 text_mode,
                                       u32 x, u32 y,
                                       struct recovered_weapon_five_marker_plan *plan)
{
    RECOVERED_SET_MARKER_TEXT_PLAN(plan, text_mode, 1U, selector + 31U);
    plan->marker_table_offset = 0x114U;
    plan->marker_start = recovered_tile_address(plan->text_plane, 0x114U, x, y);
    plan->marker_value = 0x2674U;
    plan->marker_count = 5U;
}
