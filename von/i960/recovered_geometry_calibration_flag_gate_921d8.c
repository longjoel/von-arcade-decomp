/* Paired calibration flag gate from i960 0x921d8-0x921f8. */
#include "recovered_common.h"

struct recovered_geometry_calibration_flag_gate_921d8_plan {
    recovered_u32 flag_value;
    recovered_u32 emitted_word[3];
    recovered_u32 completion_target;
    recovered_u32 helper_gate_target;
};

void recovered_geometry_calibration_flag_gate_921d8(
    recovered_u32 flag_value,
    struct recovered_geometry_calibration_flag_gate_921d8_plan *plan)
{
    plan->flag_value = flag_value;
    plan->emitted_word[0] = 0x3e4ccccdU;
    plan->emitted_word[1] = 0x3e4ccccdU;
    plan->emitted_word[2] = 0x3e4ccccdU;
    plan->completion_target = 0x9224cU;
    plan->helper_gate_target = 0x921f8U;
}
