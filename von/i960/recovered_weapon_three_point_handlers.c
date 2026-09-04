/* Shared three-point handler contract recovered from i960 0x21240-0x214b8. */
#include <stdint.h>
#include "recovered_common.h"

typedef uint32_t u32;

struct recovered_weapon_point {
    u32 x;
    u32 y;
    u32 destination;
};

struct recovered_weapon_three_point_plan {
    u32 text_helper;
    u32 text_plane;
    u32 text_column;
    u32 text_row;
    u32 text_width;
    u32 text_height;
    u32 marker_table_offset;
    struct recovered_weapon_point point[3];
};

void recovered_weapon_three_point_plan(u32 handler_kind, u32 selector,
                                       u32 text_mode, u32 asset_pointer,
                                       u32 x0, u32 y0, u32 x1, u32 y1,
                                       u32 x2, u32 y2,
                                       struct recovered_weapon_three_point_plan *plan)
{
    (void)asset_pointer;
    RECOVERED_SET_MARKER_TEXT_PLAN(plan, text_mode, 3U, selector + 31U);
    plan->marker_table_offset = handler_kind == 0U ? 0x114U
        : handler_kind == 1U ? 0x118U : 0x110U;

    plan->point[0] = (struct recovered_weapon_point){x0, y0,
        recovered_tile_address(plan->text_plane, plan->marker_table_offset, x0, y0)};
    plan->point[1] = (struct recovered_weapon_point){x1, y1,
        recovered_tile_address(plan->text_plane, plan->marker_table_offset, x1, y1)};
    plan->point[2] = (struct recovered_weapon_point){x2, y2,
        recovered_tile_address(plan->text_plane, plan->marker_table_offset, x2, y2)};
}
