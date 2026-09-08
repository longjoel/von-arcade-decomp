/* Callback timing/remainder gate recovered from i960 0x85634-0x85678. */

#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_scheduler_callback_timing_gate_85634 {
    s32 value_503a14;
    s32 value_503a18;
    s32 frame_quotient;
    s32 frame_target;
    s32 target_difference;
    u32 value_5024e8;
    u32 remainder_300;
    u32 exits_to_85678;
    u32 forces_dimensions_1_1;
};

struct recovered_scheduler_callback_timing_gate_85634
recovered_scheduler_callback_timing_gate_85634(s32 value_503a14,
                                               s32 value_503a18,
                                               u32 value_5024e8)
{
    struct recovered_scheduler_callback_timing_gate_85634 out;

    out.value_503a14 = value_503a14;
    out.value_503a18 = value_503a18;
    out.frame_quotient = value_503a14 / 48;
    out.frame_target = out.frame_quotient + 1;
    out.target_difference = value_503a18 - out.frame_target;
    out.value_5024e8 = value_5024e8;
    out.remainder_300 = value_5024e8 % 300U;
    out.exits_to_85678 = (out.target_difference >= 20
        || out.remainder_300 <= 90U) ? 1U : 0U;
    out.forces_dimensions_1_1 = out.target_difference < 20
        && out.remainder_300 > 90U ? 1U : 0U;
    return out;
}
