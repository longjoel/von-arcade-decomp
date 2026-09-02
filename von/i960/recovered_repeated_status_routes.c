/* Repeated source-or-clear status routes recovered from 0x204d0-0x20650. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_repeated_status_route_plan {
    u32 source;
    u32 source_helper;
    u32 fill_helper;
    u32 column_advance;
    u32 width;
    u32 height;
};

void recovered_repeated_status_route_plan(u32 route, u32 source_present,
                                          struct recovered_repeated_status_route_plan *plan)
{
    static const u32 sources[] = {
        0x02fcf2c8U, 0x02fcf528U, 0x02fcf828U,
        0x02fcf628U, 0x02fcf928U
    };
    plan->source = source_present && route < 5U ? sources[route] : 0U;
    plan->source_helper = source_present ? 0x0001dc10U : 0U;
    plan->fill_helper = source_present ? 0U : 0x0001df00U;
    plan->column_advance = route == 0U ? 4U : 2U;
    plan->width = route == 0U ? 8U : 12U;
    plan->height = 4U;
}
