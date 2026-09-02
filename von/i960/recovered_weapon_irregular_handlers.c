/* Handler contracts recovered from i960 0x21580-0x21780. */
#include <stdint.h>

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
    plan->text_helper = text_mode == 0U ? 0x0001dd80U : 0x0001dc10U;
    plan->text_plane = text_mode == 0U ? 0x01002000U : 0x01000000U;
    plan->text_column = 3U;
    plan->text_row = 8U;
    plan->text_width = 31U;
    plan->text_height = selector + 31U;
    plan->marker_table_offset = 0x114U;
    plan->marker_value = 0x2674U;
    plan->marker_run_count = handler_kind == 0U ? 3U : 0U;

    plan->run[0] = (struct recovered_weapon_marker_run){
        plan->text_plane + 0x114U + ((y0 << 6) + x0) * 2U,
        handler_kind == 0U ? 2U : 0U};
    plan->run[1] = (struct recovered_weapon_marker_run){
        plan->text_plane + 0x114U + ((y1 << 6) + x1) * 2U,
        handler_kind == 0U ? 4U : 0U};
    plan->run[2] = (struct recovered_weapon_marker_run){
        plan->text_plane + 0x114U + ((y2 << 6) + x2) * 2U,
        handler_kind == 0U ? 4U : 0U};
}
