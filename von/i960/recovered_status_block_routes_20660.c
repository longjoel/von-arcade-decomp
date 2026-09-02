/* Repeated status block routes recovered from i960 0x20660-0x206e8. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_status_block_route_plan {
    u32 source;
    u32 source_helper;
    u32 fill_helper;
    u32 column_comes_from_current_position;
    u32 row_comes_from_current_position;
    u32 width;
    u32 height;
};

void recovered_status_block_route_plan(u32 route, u32 source_present,
                                       struct recovered_status_block_route_plan *plan)
{
    static const u32 sources[] = {0x02fcf9e4U, 0x02fcf308U, 0x02fcf388U};
    static const u32 widths[] = {16U, 16U, 28U};
    plan->source = source_present && route < 3U ? sources[route] : 0U;
    plan->source_helper = source_present ? 0x0001dc10U : 0U;
    plan->fill_helper = source_present ? 0U : 0x0001df00U;
    plan->column_comes_from_current_position = 1U;
    plan->row_comes_from_current_position = 1U;
    plan->width = route < 3U ? widths[route] : 0U;
    plan->height = 4U;
}
