/* Attributed status routes recovered from i960 0x20840-0x209b8. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_attributed_status_route_plan {
    u32 source;
    u32 helper;
    u32 width;
    u32 height;
    u32 column_comes_from_current_position;
    u32 row_comes_from_current_position;
};

void recovered_attributed_status_route_plan(u32 route, u32 source_present,
                                            u32 caller_g5, u32 caller_g3,
                                            struct recovered_attributed_status_route_plan *plan)
{
    static const u32 sources[] = {
        0x02fcfa64U, 0x02fcfbe4U, 0x02fcfdd4U, 0x02fd0014U,
        0x02fd0124U, 0x02fd02e4U, 0x02fd0464U, 0x02fd0634U
    };
    plan->source = source_present && route < 8U ? sources[route] : 0U;
    plan->helper = source_present ? 0x0001dc90U : 0x0001df00U;
    plan->width = route == 0U ? 24U : route == 1U ? 31U
        : route == 2U ? caller_g5 + 31U : route == 3U ? caller_g3 + 31U
        : route == 4U ? 28U : route == 5U ? 24U : 29U;
    plan->height = route == 3U ? 4U : 8U;
    plan->column_comes_from_current_position = 1U;
    plan->row_comes_from_current_position = 1U;
}
