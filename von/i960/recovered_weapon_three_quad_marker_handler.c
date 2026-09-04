/* Handler contract recovered from i960 0x21784-0x2189c. */
#include <stdint.h>
#include "recovered_common.h"

typedef uint32_t u32;

struct recovered_weapon_quad_marker_run {
    u32 start;
    u32 count;
};

struct recovered_weapon_three_quad_marker_plan {
    u32 text_helper;
    u32 text_plane;
    u32 text_column;
    u32 text_row;
    u32 text_width;
    u32 text_height;
    u32 marker_table_offset;
    struct recovered_weapon_quad_marker_run run[3];
};

void recovered_weapon_three_quad_marker_plan(
    u32 selector, u32 text_mode,
    u32 x0, u32 y0, u32 x1, u32 y1, u32 x2, u32 y2,
    struct recovered_weapon_three_quad_marker_plan *plan)
{
    RECOVERED_SET_MARKER_TEXT_PLAN(plan, text_mode, 2U, selector + 31U);
    plan->marker_table_offset = 0x110U;
    plan->run[0] = (struct recovered_weapon_quad_marker_run){
        recovered_tile_address(plan->text_plane, 0x110U, x0, y0), 4U};
    plan->run[1] = (struct recovered_weapon_quad_marker_run){
        recovered_tile_address(plan->text_plane, 0x110U, x1, y1), 4U};
    plan->run[2] = (struct recovered_weapon_quad_marker_run){
        recovered_tile_address(plan->text_plane, 0x110U, x2, y2), 4U};
}
