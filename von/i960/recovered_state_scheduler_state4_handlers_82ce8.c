/* State-4 scheduler handlers recovered from i960 0x82ce8-0x82d18. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_scheduler_state4_handler {
    u32 handled;
    u32 value_504d98;
    u32 write_504d80;
    u32 value_504d80;
};

struct recovered_state_scheduler_state4_handler
recovered_state_scheduler_state4_handler(u32 entry, u32 object_state)
{
    struct recovered_state_scheduler_state4_handler out = {0U, 0U, 0U, 0U};

    if (entry == 0x82ce8U) {
        out.handled = 1U;
        if (object_state == 4U) {
            out.value_504d98 = 3U;
            out.write_504d80 = 1U;
            out.value_504d80 = 28U;
        } else {
            out.value_504d98 = 2U;
        }
    } else if (entry == 0x82d04U) {
        out.handled = 1U;
        out.value_504d98 = object_state == 4U ? 2U : 3U;
    }
    return out;
}
