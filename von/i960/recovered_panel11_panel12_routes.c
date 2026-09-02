/* Panel routes recovered from i960 0x1fdf0 and 0x1fe60. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_panel11_plan {
    u32 first_source;
    u32 first_helper;
    u32 second_source;
    u32 second_helper;
    u32 column;
    u32 row;
    u32 width;
    u32 height;
};

struct recovered_panel12_plan {
    u32 source;
    u32 source_helper;
    u32 fill_helper;
    u32 column_comes_from_current_position;
    u32 row_comes_from_current_position;
    u32 width;
    u32 height;
};

void recovered_panel11_plan(struct recovered_panel11_plan *plan)
{
    plan->first_source = 0x02fd892eU;
    plan->first_helper = 0x0001dc90U;
    plan->second_source = 0x02fd894aU;
    plan->second_helper = 0x0001dc10U;
    plan->column = 20U;
    plan->row = 20U;
    plan->width = 7U;
    plan->height = 2U;
}

void recovered_panel12_plan(u32 source_present,
                            struct recovered_panel12_plan *plan)
{
    plan->source = source_present ? 0x02fe0cb0U : 0U;
    plan->source_helper = source_present ? 0x0001dc10U : 0U;
    plan->fill_helper = source_present ? 0U : 0x0001df00U;
    plan->column_comes_from_current_position = 1U;
    plan->row_comes_from_current_position = 1U;
    plan->width = 20U;
    plan->height = 2U;
}
