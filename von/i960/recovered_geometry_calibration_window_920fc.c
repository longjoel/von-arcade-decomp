/* Fixed paired-calibration response window from i960 0x920fc-0x92144. */
#include "recovered_common.h"

struct recovered_geometry_calibration_window_920fc_plan {
    recovered_u32 window_word[4];
    recovered_u32 control_address;
    recovered_u32 control_value;
    recovered_u32 publish_address;
    recovered_u32 completion_word;
};

void recovered_geometry_calibration_window_920fc(
    struct recovered_geometry_calibration_window_920fc_plan *plan)
{
    plan->window_word[0] = 0x403968U;
    plan->window_word[1] = 0x4039f0U;
    plan->window_word[2] = 0x850225U;
    plan->window_word[3] = 0U;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->publish_address = 0x804000U;
    plan->completion_word = 6U;
}
