/* Non-state helper consumer recovered from i960 0x841ec-0x84228. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_scheduler_nonstate_handler_841ec {
    u32 value_504d80;
};

struct recovered_state_scheduler_nonstate_handler_841ec
recovered_state_scheduler_nonstate_handler_841ec(int32_t helper_value,
                                                u32 mode_504e30,
                                                u32 incoming_g2)
{
    struct recovered_state_scheduler_nonstate_handler_841ec out = {33U};
    (void)incoming_g2;

    if (helper_value < 4 && (mode_504e30 & 0x4U) != 0U) {
        out.value_504d80 = 32U;
    } else if (helper_value > 0 && (mode_504e30 & 0x2U) != 0U) {
        out.value_504d80 = 37U;
    }
    return out;
}
