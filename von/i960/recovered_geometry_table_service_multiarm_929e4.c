/* Three-arm indexed table dispatcher from i960 0x929e4-0x92da0. */
#include "recovered_common.h"

struct recovered_geometry_table_service_multiarm_929e4_plan {
    recovered_u32 source_value;
    recovered_u32 threshold_value;
    recovered_u32 guard_value[3];
    recovered_u32 arm_target[3];
    recovered_u32 adjusted_packet_source[3];
    recovered_u32 operand_word[3];
    recovered_u32 selected_arm;
    recovered_u32 selected_source;
    recovered_u32 selected_operand;
    recovered_u32 completion_target;
};

void recovered_geometry_table_service_multiarm_929e4(
    recovered_u32 source_value,
    struct recovered_geometry_table_service_multiarm_929e4_plan *plan)
{
    static const recovered_u32 guard_subtract[3] = {0x3cU, 0x46U, 0x50U};
    static const recovered_u32 packet_subtract[3] = {0U, 10U, 20U};
    static const recovered_u32 target[3] = {0x929fcU, 0x92b2cU, 0x92c5cU};
    static const recovered_u32 operand[3] = {0xb800U, 0xc000U, 0xc800U};
    recovered_u32 selected_arm = 3U;

    plan->source_value = source_value;
    plan->threshold_value = 15U << 3;
    for (unsigned i = 0; i < 3; ++i) {
        plan->guard_value[i] = source_value - guard_subtract[i];
        plan->arm_target[i] = target[i];
        plan->adjusted_packet_source[i] = source_value - packet_subtract[i];
        plan->operand_word[i] = operand[i];
        if (selected_arm == 3U && plan->guard_value[i] <= plan->threshold_value)
            selected_arm = i;
    }
    plan->selected_arm = selected_arm;
    plan->selected_source = selected_arm < 3U
        ? plan->adjusted_packet_source[selected_arm] : 0U;
    plan->selected_operand = selected_arm < 3U
        ? plan->operand_word[selected_arm] : 0U;
    plan->completion_target = 0x92d84U;
}
