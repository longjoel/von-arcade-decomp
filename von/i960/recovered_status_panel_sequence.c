/* Three-stage status-panel sequence recovered from i960 0x1f540. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_status_panel_stage {
    u32 helper;
    u32 source;
    u32 fill_value;
    u32 column;
    u32 row;
    u32 width;
    u32 height;
};

struct recovered_status_panel_sequence_plan {
    struct recovered_status_panel_stage first;
    struct recovered_status_panel_stage second;
    struct recovered_status_panel_stage third;
};

void recovered_status_panel_sequence_plan(u32 initial_column, u32 initial_row,
                                          u32 source_mode, u32 fill_mode,
                                          struct recovered_status_panel_sequence_plan *plan)
{
    u32 first_column = initial_column + 2U;
    u32 first_row = initial_row - 1U;
    u32 second_column = first_column + 12U;
    u32 second_row = first_row - 7U;

    plan->first.helper = source_mode ? 0x0001dc10U : 0x0001dc90U;
    plan->first.source = 0x02fde9d0U;
    plan->first.fill_value = 0U;
    plan->first.column = first_column;
    plan->first.row = first_row;
    plan->first.width = 55U;
    plan->first.height = 8U;

    plan->second.helper = 0x0001dc10U;
    plan->second.source = 0x02fe1606U;
    plan->second.fill_value = 0U;
    plan->second.column = second_column;
    plan->second.row = second_row;
    plan->second.width = 34U;
    plan->second.height = 2U;

    plan->third.helper = fill_mode ? 0x0001df00U : 0x0001dc90U;
    plan->third.source = fill_mode ? 0U : 0x02fe158eU;
    plan->third.fill_value = 0U;
    plan->third.column = second_column;
    plan->third.row = second_row;
    plan->third.width = 30U;
    plan->third.height = 2U;
}
