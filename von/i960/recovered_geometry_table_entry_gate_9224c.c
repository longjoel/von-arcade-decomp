/* Indexed geometry-service entry gate from i960 0x9224c-0x9225c. */
#include "recovered_common.h"

struct recovered_geometry_table_entry_gate_9224c_plan {
    recovered_u32 source_value;
    recovered_u32 threshold_value;
    recovered_u32 normal_target;
    recovered_u32 high_target;
};

void recovered_geometry_table_entry_gate_9224c(
    recovered_u32 source_value,
    struct recovered_geometry_table_entry_gate_9224c_plan *plan)
{
    plan->source_value = source_value;
    plan->threshold_value = 0x12cU;
    plan->normal_target = 0x9225cU;
    plan->high_target = 0x92380U;
}
