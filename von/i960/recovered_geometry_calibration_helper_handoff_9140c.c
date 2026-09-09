/* Calibration helper handoff from i960 0x9140c-0x91434. */
#include "recovered_common.h"

struct recovered_geometry_calibration_helper_handoff_9140c_plan {
    recovered_u32 helper_target;
    recovered_u32 first_table_address;
    recovered_u32 second_table_address;
    recovered_u32 first_context_word;
    recovered_u32 second_context_word;
    recovered_u32 completion_word;
};

void recovered_geometry_calibration_helper_handoff_9140c(
    recovered_u32 first_context_word, recovered_u32 second_context_word,
    struct recovered_geometry_calibration_helper_handoff_9140c_plan *plan)
{
    plan->helper_target = 0x8e310U;
    plan->first_table_address = 0x2be2cb4U;
    plan->second_table_address = 0x2be2d2cU;
    plan->first_context_word = first_context_word;
    plan->second_context_word = second_context_word;
    plan->completion_word = 6U;
}
