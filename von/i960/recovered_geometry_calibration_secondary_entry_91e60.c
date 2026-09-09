/* Second paired-calibration entry prologue from i960 0x91e60-0x91e98. */
#include "recovered_common.h"

struct recovered_geometry_calibration_secondary_entry_91e60_input {
    recovered_u32 argument_g0;
    recovered_u32 argument_g1;
    recovered_u32 argument_g2;
    recovered_u32 source_value;
};

struct recovered_geometry_calibration_secondary_entry_91e60_plan {
    recovered_u32 saved_g2;
    recovered_u32 source_value;
    recovered_u32 threshold_value;
    recovered_u32 table_base;
    recovered_u32 table_address;
    recovered_u32 preserved_g0;
    recovered_u32 preserved_g1;
    recovered_u32 preserved_g2;
    recovered_u32 first_partition_target;
    recovered_u32 upper_partition_target;
};

void recovered_geometry_calibration_secondary_entry_91e60(
    const struct recovered_geometry_calibration_secondary_entry_91e60_input *input,
    struct recovered_geometry_calibration_secondary_entry_91e60_plan *plan)
{
    plan->saved_g2 = input->argument_g2;
    plan->source_value = input->source_value;
    plan->threshold_value = 0x12bU;
    plan->table_base = 0x2b46134U;
    plan->table_address = 0x2b80f64U;
    plan->preserved_g0 = input->argument_g0;
    plan->preserved_g1 = input->argument_g1;
    plan->preserved_g2 = input->argument_g2;
    plan->first_partition_target = 0x91e98U;
    plan->upper_partition_target = 0x91eccU;
}
