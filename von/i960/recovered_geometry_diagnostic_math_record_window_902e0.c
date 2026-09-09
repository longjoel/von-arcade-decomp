/* Record response window from i960 0x902e0-0x90398. */
#include "recovered_common.h"

struct recovered_geometry_diagnostic_math_record_window_902e0_plan {
    recovered_u32 state_word;
    recovered_u32 window_word[4];
    recovered_u32 zero_word[3];
    recovered_u32 nonzero_word[3];
    recovered_u32 control_address;
    recovered_u32 control_value;
    recovered_u32 publish_address;
    recovered_u32 completion_word[2];
    recovered_u32 completion_count;
    recovered_u32 call_target;
};

void recovered_geometry_diagnostic_math_record_window_902e0(
    recovered_u32 state_word, const recovered_u32 zero_word[3],
    const recovered_u32 nonzero_word[3], recovered_u32 frame_word,
    struct recovered_geometry_diagnostic_math_record_window_902e0_plan *plan)
{
    plan->state_word = state_word;
    for (unsigned i = 0; i < 3; ++i) {
        plan->zero_word[i] = zero_word[i];
        plan->nonzero_word[i] = nonzero_word[i];
        plan->window_word[i] = state_word == 0U ? zero_word[i] : nonzero_word[i];
    }
    plan->window_word[3] = state_word == 0U ? 0U : frame_word;
    plan->control_address = 0x800010U;
    plan->control_value = 0x101U;
    plan->publish_address = 0x804000U;
    plan->completion_word[0] = 6U;
    plan->completion_word[1] = 6U;
    plan->completion_count = 2U;
    plan->call_target = 0x6fec0U;
}
