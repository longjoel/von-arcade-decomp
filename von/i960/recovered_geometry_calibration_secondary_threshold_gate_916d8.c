/* First paired-calibration threshold gate from i960 0x916d8-0x916e0. */
#include "recovered_common.h"

struct recovered_geometry_calibration_secondary_threshold_gate_916d8_plan {
    recovered_u32 source_value;
    recovered_u32 threshold_value;
    recovered_u32 low_path_target;
    recovered_u32 high_path_target;
};

void recovered_geometry_calibration_secondary_threshold_gate_916d8(
    recovered_u32 source_value,
    struct recovered_geometry_calibration_secondary_threshold_gate_916d8_plan *plan)
{
    plan->source_value = source_value;
    plan->threshold_value = 0x8bU;
    plan->low_path_target = 0x91a74U;
    plan->high_path_target = 0x9174cU;
}
