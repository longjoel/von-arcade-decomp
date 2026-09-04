/* Handler contracts recovered from i960 0x21580-0x21780. */
#include <stdint.h>
#include "recovered_common.h"

typedef uint32_t u32;

struct recovered_weapon_marker_run {
    u32 start;
    u32 count;
};

struct recovered_weapon_irregular_handler_plan {
    u32 text_helper;
    u32 text_plane;
    u32 text_column;
    u32 text_row;
    u32 text_width;
    u32 text_height;
    u32 marker_table_offset;
    u32 marker_value;
    u32 marker_run_count;
    struct recovered_weapon_marker_run run[3];
};

void recovered_weapon_irregular_handler_plan(
    u32 handler_kind, u32 selector, u32 text_mode,
    u32 x0, u32 y0, u32 x1, u32 y1, u32 x2, u32 y2,
    struct recovered_weapon_irregular_handler_plan *plan)
{
    RECOVERED_SET_MARKER_TEXT_PLAN(plan, text_mode, 3U, selector + 31U);
    plan->marker_table_offset = 0x114U;
    plan->marker_value = 0x2674U;
    plan->marker_run_count = handler_kind == 0U ? 3U : 0U;

    plan->run[0] = (struct recovered_weapon_marker_run){
        recovered_tile_address(plan->text_plane, 0x114U, x0, y0),
        handler_kind == 0U ? 2U : 0U};
    plan->run[1] = (struct recovered_weapon_marker_run){
        recovered_tile_address(plan->text_plane, 0x114U, x1, y1),
        handler_kind == 0U ? 4U : 0U};
    plan->run[2] = (struct recovered_weapon_marker_run){
        recovered_tile_address(plan->text_plane, 0x114U, x2, y2),
        handler_kind == 0U ? 4U : 0U};
}
