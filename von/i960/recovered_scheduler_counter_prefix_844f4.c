/* Counter/dispatch prefix recovered from i960 0x844f4-0x84524. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_counter_prefix_844f4 {
    u32 slot;
    u32 jumped_to_847b0;
    u32 writes_509a68;
    u32 value_509a68;
};

struct recovered_scheduler_counter_prefix_844f4
recovered_scheduler_counter_prefix_844f4(u32 value_5024e8,
                                         u32 value_509a68)
{
    struct recovered_scheduler_counter_prefix_844f4 out = {
        value_5024e8 & 3U, 0U, 0U, value_509a68
    };

    if (out.slot != 0U) {
        out.jumped_to_847b0 = 1U;
        return out;
    }
    out.writes_509a68 = 1U;
    out.value_509a68 = value_509a68 + 1U;
    if (out.value_509a68 > 59U)
        out.value_509a68 -= 60U;
    return out;
}
