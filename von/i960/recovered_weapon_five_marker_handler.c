/* Handler contract recovered from i960 0x214bc-0x2157c. */
#include <stdint.h>

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
    plan->text_helper = text_mode == 0U ? 0x0001dd80U : 0x0001dc10U;
    plan->text_plane = text_mode == 0U ? 0x01002000U : 0x01000000U;
    plan->text_column = 1U;
    plan->text_row = 8U;
    plan->text_width = 31U;
    plan->text_height = selector + 31U;
    plan->marker_table_offset = 0x114U;
    plan->marker_start = plan->text_plane + 0x114U + ((y << 6) + x) * 2U;
    plan->marker_value = 0x2674U;
    plan->marker_count = 5U;
}
