/* Shared three-point handler contract recovered from i960 0x21240-0x214b8. */
#include <stdint.h>

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
    plan->text_helper = text_mode == 0U ? 0x0001dd80U : 0x0001dc10U;
    plan->text_plane = text_mode == 0U ? 0x01002000U : 0x01000000U;
    plan->text_column = 3U;
    plan->text_row = 8U;
    plan->text_width = 31U;
    plan->text_height = selector + 31U;
    plan->marker_table_offset = handler_kind == 0U ? 0x114U
        : handler_kind == 1U ? 0x118U : 0x110U;

    plan->point[0] = (struct recovered_weapon_point){x0, y0,
        plan->text_plane + plan->marker_table_offset + ((y0 << 6) + x0) * 2U};
    plan->point[1] = (struct recovered_weapon_point){x1, y1,
        plan->text_plane + plan->marker_table_offset + ((y1 << 6) + x1) * 2U};
    plan->point[2] = (struct recovered_weapon_point){x2, y2,
        plan->text_plane + plan->marker_table_offset + ((y2 << 6) + x2) * 2U};
}
