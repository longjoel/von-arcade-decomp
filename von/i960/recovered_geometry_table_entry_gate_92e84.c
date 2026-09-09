/* Threshold entry gate from i960 0x92e84-0x92e9c. */
#include "recovered_common.h"

struct recovered_geometry_table_entry_gate_92e84_plan {
    recovered_u32 source_value;
    recovered_u32 threshold_value;
    recovered_u32 adjusted_value;
    recovered_u32 selected_target;
    recovered_u32 packet_target;
    recovered_u32 fallback_target;
};

void recovered_geometry_table_entry_gate_92e84(
    recovered_u32 source_value, recovered_u32 g7,
    struct recovered_geometry_table_entry_gate_92e84_plan *plan)
{
    plan->source_value = source_value;
    plan->threshold_value = 15U << 3;
    plan->adjusted_value = g7 - 0x3cU;
    plan->packet_target = 0x92e9cU;
    plan->fallback_target = 0x92fc0U;
    plan->selected_target = plan->adjusted_value > plan->threshold_value
        ? plan->fallback_target : plan->packet_target;
}
