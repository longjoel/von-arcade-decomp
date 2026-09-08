/* Ratio/status prefix recovered from i960 0x83348-0x833dc. */

#include <math.h>
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_scheduler_ratio_prefix_83310 {
    u32 value_504e1c;
    u32 mode_504e30;
    u32 mode_changed;
    u32 random_table_dispatch;
    u32 random_table_target;
};

static const u32 random_targets[5] = {
    0x833dcU, 0x833e8U, 0x833f8U, 0x83408U, 0x83418U
};

struct recovered_state_scheduler_ratio_prefix_83310
recovered_state_scheduler_ratio_prefix_83310(double ratio,
                                             u32 mode_504e30,
                                             u32 state_504d7c,
                                             u32 random_remainder_5)
{
    struct recovered_state_scheduler_ratio_prefix_83310 out = {
        1U, mode_504e30, 0U, 0U, 0U
    };

    if (ratio <= 0.9)
        return out;
    if ((out.mode_504e30 & 0x4U) != 0U) {
        out.mode_504e30 &= ~0x4U;
        out.mode_changed = 1U;
    }
    if (state_504d7c != 5U)
        return out;
    out.random_table_dispatch = 1U;
    out.random_table_target = random_targets[random_remainder_5 % 5U];
    return out;
}
