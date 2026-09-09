/* Remaining threshold gates in the indexed table chain at 0x92fc0/0x930f0. */
#include "recovered_common.h"

struct recovered_geometry_table_threshold_gate_plan {
    recovered_u32 source_value;
    recovered_u32 threshold_value;
    recovered_u32 adjusted_value;
    recovered_u32 selected_target;
    recovered_u32 packet_target;
    recovered_u32 fallback_target;
};

static void recovered_geometry_table_threshold_gate(
    recovered_u32 source_value, recovered_u32 g7, recovered_u32 subtract_value,
    recovered_u32 packet_target, recovered_u32 fallback_target,
    struct recovered_geometry_table_threshold_gate_plan *plan)
{
    plan->source_value = source_value;
    plan->threshold_value = 15U << 3;
    plan->adjusted_value = g7 - subtract_value;
    plan->packet_target = packet_target;
    plan->fallback_target = fallback_target;
    plan->selected_target = plan->adjusted_value > plan->threshold_value
        ? plan->fallback_target : plan->packet_target;
}

void recovered_geometry_table_entry_gate_92fc0(
    recovered_u32 source_value, recovered_u32 g7,
    struct recovered_geometry_table_threshold_gate_plan *plan)
{
    recovered_geometry_table_threshold_gate(
        source_value, g7, 0x46U, 0x92fccU, 0x930f0U, plan);
}

void recovered_geometry_table_entry_gate_930f0(
    recovered_u32 source_value, recovered_u32 g7,
    struct recovered_geometry_table_threshold_gate_plan *plan)
{
    recovered_geometry_table_threshold_gate(
        source_value, g7, 0x50U, 0x930fcU, 0x93224U, plan);
}
