/* Flag finalizer recovered from i960 0x84470-0x844f0. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_flag_finalize_84470 {
    u32 value_509a60;
    u32 set_bit6;
    u32 set_bit7;
};

struct recovered_scheduler_flag_finalize_84470
recovered_scheduler_flag_finalize_84470(u32 value_509a60)
{
    struct recovered_scheduler_flag_finalize_84470 out = {
        value_509a60, 0U, 0U
    };

    if ((value_509a60 & (1U << 5)) != 0U
        && (value_509a60 & (1U << 1)) != 0U) {
        out.value_509a60 |= 1U << 7;
        out.set_bit7 = 1U;
    } else if (((value_509a60 & (1U << 4)) != 0U
                && (value_509a60 & ((1U << 0) | (1U << 1))) != 0U)
               || ((value_509a60 & (1U << 5)) != 0U
                   && (value_509a60 & (1U << 0)) != 0U)) {
        out.value_509a60 |= 1U << 6;
        out.set_bit6 = 1U;
    }
    return out;
}
