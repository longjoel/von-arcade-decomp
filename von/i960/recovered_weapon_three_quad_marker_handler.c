/* Handler contract recovered from i960 0x21784-0x2189c. */
#include <stdint.h>

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
    plan->text_helper = text_mode == 0U ? 0x0001dd80U : 0x0001dc10U;
    plan->text_plane = text_mode == 0U ? 0x01002000U : 0x01000000U;
    plan->text_column = 2U;
    plan->text_row = 8U;
    plan->text_width = 31U;
    plan->text_height = selector + 31U;
    plan->marker_table_offset = 0x110U;
    plan->run[0] = (struct recovered_weapon_quad_marker_run){
        plan->text_plane + 0x110U + ((y0 << 6) + x0) * 2U, 4U};
    plan->run[1] = (struct recovered_weapon_quad_marker_run){
        plan->text_plane + 0x110U + ((y1 << 6) + x1) * 2U, 4U};
    plan->run[2] = (struct recovered_weapon_quad_marker_run){
        plan->text_plane + 0x110U + ((y2 << 6) + x2) * 2U, 4U};
}
