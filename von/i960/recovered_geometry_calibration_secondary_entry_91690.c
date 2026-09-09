/* Paired calibration entry gate from i960 0x91690-0x916d8. */
#include "recovered_common.h"

struct recovered_geometry_calibration_secondary_entry_91690_input {
    recovered_u32 argument_g0;
    recovered_u32 argument_g1;
    recovered_u32 argument_g2;
    recovered_u32 incoming_g14;
    recovered_u32 source_value;
    recovered_u32 g28_value;
};

struct recovered_geometry_calibration_secondary_entry_91690_plan {
    recovered_u32 saved_g2;
    recovered_u32 saved_g14;
    recovered_u32 source_value;
    recovered_u32 threshold_limit;
    recovered_u32 table_base;
    recovered_u32 table_address;
    recovered_u32 preserved_g0;
    recovered_u32 preserved_g1;
    recovered_u32 first_target;
    recovered_u32 threshold_partition_target;
};

void recovered_geometry_calibration_secondary_entry_91690(
    const struct recovered_geometry_calibration_secondary_entry_91690_input *input,
    struct recovered_geometry_calibration_secondary_entry_91690_plan *plan)
{
    plan->saved_g2 = input->argument_g2;
    plan->saved_g14 = input->incoming_g14;
    plan->source_value = input->source_value;
    plan->threshold_limit = input->g28_value + 31U;
    plan->table_base = 0x2b46134U;
    plan->table_address = 0x2b80f64U;
    plan->preserved_g0 = input->argument_g0;
    plan->preserved_g1 = input->argument_g1;
    plan->first_target = 0x91a74U;
    plan->threshold_partition_target = 0x916d8U;
}
