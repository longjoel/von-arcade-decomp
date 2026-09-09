/* Random-helper consumer recovered from i960 0x84150-0x8419c. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_scheduler_random_handler_84150 {
    u32 write_504d80;
    u32 value_504d80;
};

struct recovered_state_scheduler_random_handler_84150
recovered_state_scheduler_random_handler_84150(int32_t helper_value,
                                               u32 mode_504e30,
                                               u32 incoming_g2)
{
    struct recovered_state_scheduler_random_handler_84150 out = {1U, 33U};
    (void)incoming_g2;

    if (helper_value > 4 && (mode_504e30 & 0x4U) != 0U) {
        out.value_504d80 = 32U;
    } else if (helper_value > 0 && (mode_504e30 & 0x2U) != 0U) {
        out.value_504d80 = 37U;
    }
    return out;
}
