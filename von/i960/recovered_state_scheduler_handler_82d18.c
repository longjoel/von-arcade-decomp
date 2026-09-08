/* Scheduler handler recovered from i960 0x82d18-0x82d34. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_scheduler_handler_82d18 {
    u32 write_504d98;
    u32 value_504d98;
    u32 write_504d80;
    u32 value_504d80;
};

struct recovered_state_scheduler_handler_82d18
recovered_state_scheduler_handler_82d18(u32 object_state)
{
    struct recovered_state_scheduler_handler_82d18 out = {0U, 0U, 1U, 8U};

    if (object_state == 8U) {
        out.write_504d98 = 1U;
        out.value_504d98 = 3U;
        out.value_504d80 = 20U;
    }
    return out;
}
