/* Common scheduler tail recovered from i960 0x82d74-0x82da4. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_scheduler_tail_82d74 {
    u32 value_504d80;
    u32 value_504d84;
    u32 value_504d88;
    u32 value_504d8c;
    u32 write_504d90;
    u32 value_504d90;
};

struct recovered_state_scheduler_tail_82d74
recovered_state_scheduler_tail_82d74(u32 value_504d80, u32 value_504d84,
                                     u32 value_504d88, u32 value_504d8c)
{
    struct recovered_state_scheduler_tail_82d74 out = {
        value_504d80, 0U, value_504d88, value_504d8c, 0U, 0U
    };

    /* The loaded second word is deliberately overwritten with zero. */
    (void)value_504d84;

    if (value_504d80 <= 6U || value_504d80 == 8U) {
        out.write_504d90 = 1U;
        out.value_504d90 = 15U;
    }
    return out;
}
