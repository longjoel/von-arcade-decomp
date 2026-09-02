/* Attributed status routes recovered from i960 0x209c0-0x20a18. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_attributed_status_route_209c0_plan {
    u32 source;
    u32 helper;
    u32 width;
    u32 height;
    u32 column_comes_from_current_position;
    u32 row_comes_from_current_position;
};

void recovered_attributed_status_route_209c0_plan(
    u32 route, u32 source_present,
    struct recovered_attributed_status_route_209c0_plan *plan)
{
    static const u32 sources[] = { 0x02fd09a4U, 0x02fd07f4U };
    static const u32 widths[] = { 28U, 27U };

    plan->source = source_present && route < 2U ? sources[route] : 0U;
    plan->helper = source_present ? 0x0001dc90U : 0x0001df00U;
    plan->width = route < 2U ? widths[route] : 0U;
    plan->height = 8U;
    plan->column_comes_from_current_position = 1U;
    plan->row_comes_from_current_position = 1U;
}
