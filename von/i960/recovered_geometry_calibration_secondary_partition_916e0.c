/* Paired calibration threshold partition from i960 0x916e0-0x91a74. */
#include "recovered_common.h"

struct recovered_geometry_calibration_secondary_partition_916e0_plan {
    recovered_u32 source_value;
    recovered_u32 branch_target;
    recovered_u32 branch_class;
};

void recovered_geometry_calibration_secondary_partition_916e0(
    recovered_u32 source_value,
    struct recovered_geometry_calibration_secondary_partition_916e0_plan *plan)
{
    recovered_u32 target;
    recovered_u32 branch_class;

    if (source_value <= 0x8bU) {
        target = 0x91a74U;
        branch_class = 0U;
    } else if (source_value <= 0x9fU) {
        target = 0x9174cU;
        branch_class = 1U;
    } else if (source_value <= 0xb3U) {
        target = 0x917b8U;
        branch_class = 2U;
    } else if (source_value <= 0xb8U) {
        target = 0x91a74U;
        branch_class = 3U;
    } else if (source_value <= 0xccU) {
        target = 0x91818U;
        branch_class = 4U;
    } else if (source_value <= 0xf4U) {
        target = 0x91850U;
        branch_class = 5U;
    } else if (source_value <= 0x108U) {
        target = 0x91878U;
        branch_class = 6U;
    } else if (source_value <= 0x11cU) {
        target = 0x918a0U;
        branch_class = 7U;
    } else if (source_value <= 0x1f8U) {
        target = 0x918f8U;
        branch_class = 8U;
    } else if (source_value <= 0x234U) {
        target = 0x91920U;
        branch_class = 9U;
    } else if (source_value <= 0x270U) {
        target = 0x91940U;
        branch_class = 10U;
    } else if (source_value <= 0x284U) {
        target = 0x91964U;
        branch_class = 11U;
    } else if (source_value <= 0x2c0U) {
        target = 0x9198cU;
        branch_class = 12U;
    } else if (source_value <= 0x2d4U) {
        target = 0x919b0U;
        branch_class = 13U;
    } else if (source_value <= 0x310U) {
        target = 0x919d0U;
        branch_class = 14U;
    } else if (source_value <= 0x315U) {
        target = 0x91a74U;
        branch_class = 15U;
    } else if (source_value <= 0x379U) {
        target = 0x919e0U;
        branch_class = 16U;
    } else {
        target = 0x91a74U;
        branch_class = 17U;
    }

    plan->source_value = source_value;
    plan->branch_target = target;
    plan->branch_class = branch_class;
}
