/* Grid initializer recovered from i960 0x227b0-0x2283c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_status_grid_cell {
    u32 column;
    u32 row;
};

struct recovered_status_grid_initializer_plan {
    u32 selected;
    u32 period;
    u32 remainder;
    u32 source;
    u32 first_helper;
    u32 second_helper;
    u32 width;
    u32 height;
    u32 cell_count;
    struct recovered_status_grid_cell cell[32];
};

void recovered_status_grid_initializer_plan(
    u32 phase, struct recovered_status_grid_initializer_plan *plan)
{
    plan->period = 3U << 6;
    plan->remainder = phase % plan->period;
    plan->selected = plan->remainder == 0U ? 1U : 0U;
    plan->source = 0x02fe8fc4U;
    plan->first_helper = 0x0001de80U;
    plan->second_helper = 0x0001de00U;
    plan->width = 16U;
    plan->height = 8U;
    plan->cell_count = 32U;

    u32 index = 0U;
    for (u32 row = 0; row < 8U; ++row) {
        for (u32 column = 0; column < 4U; ++column) {
            plan->cell[index++] = (struct recovered_status_grid_cell){
                column << 4, row << 3};
        }
    }
}
