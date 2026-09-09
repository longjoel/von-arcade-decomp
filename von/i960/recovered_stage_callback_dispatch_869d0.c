/* Stage callback dispatch plan recovered from i960 0x869d0-0x86a88. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_callback_dispatch_869d0 {
    u32 saved_input;
    u32 frame_builder_target;
    u32 helper_argument0;
    u32 helper_argument1;
    u32 helper_target;
    u32 selector;
    u32 descriptor;
    u32 target;
    u32 returns;
};

struct recovered_stage_callback_dispatch_869d0
recovered_stage_callback_dispatch_869d0(u32 input_g0, u32 selector)
{
    struct recovered_stage_callback_dispatch_869d0 out;

    /* The call at 0x85b00 consumes live r7/r5/r6/g7 inputs; g0 is only
     * saved in r4 and restored as g1 for the following helper call. */
    out.saved_input = input_g0;
    out.frame_builder_target = 0x00085b00U;
    out.helper_argument0 = 10U;
    out.helper_argument1 = input_g0;
    out.helper_target = 0x0001cac8U;
    out.selector = selector;
    out.descriptor = 0U;
    out.target = 0U;
    out.returns = 0U;
    if (selector > 6U) {
        out.returns = 1U;
        return out;
    }

    out.descriptor = (selector & 1U) == 0U ?
        0x000869c8U : 0x000869caU;
    switch (selector) {
    case 0U:
        out.target = 0x0001d7d0U;
        break;
    case 1U:
        out.target = 0x0001d9e0U;
        break;
    case 2U:
        out.target = 0x0001d9e0U;
        break;
    case 3U:
        out.target = 0x0001d880U;
        break;
    case 4U:
        out.target = 0x0001d880U;
        break;
    case 5U:
        out.target = 0x0001d930U;
        break;
    default:
        out.target = 0x0001d930U;
        break;
    }
    return out;
}
