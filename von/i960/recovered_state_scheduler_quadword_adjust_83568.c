/* Non-state quadword adjustment recovered from i960 0x83568-0x835e0. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_scheduler_quadword_adjust_83568 {
    int32_t remainder_8;
    u32 value_504d80;
    u32 value_504d84;
    u32 write_quadword;
    u32 write_504d90;
    u32 value_504d90;
};

struct recovered_state_scheduler_quadword_adjust_83568
recovered_state_scheduler_quadword_adjust_83568(int32_t random_value,
                                               u32 old_value_504d80,
                                               u32 old_value_504d84,
                                               u32 control_504e30)
{
    int32_t adjusted = random_value;
    int32_t block;
    int32_t remainder;
    u32 delta;
    struct recovered_state_scheduler_quadword_adjust_83568 out;

    if (adjusted < 0)
        adjusted += 7;
    block = adjusted & ~7;
    remainder = random_value - block;
    if (remainder >= 3) {
        delta = 2U;
    } else if ((control_504e30 & 4U) != 0U) {
        /* The bit-2 arm precedes the sign split in the image. */
        delta = 1U;
    } else if (remainder <= 0) {
        delta = 2U;
    } else {
        delta = (control_504e30 & 2U) != 0U ? 7U : 2U;
    }
    out.remainder_8 = remainder;
    out.value_504d80 = old_value_504d80 + delta;
    out.value_504d84 = old_value_504d84;
    out.write_quadword = 1U;
    out.write_504d90 = 1U;
    out.value_504d90 = 15U;
    return out;
}
