/* Scheduler handler recovered from i960 0x82c6c-0x82cb0. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_scheduler_handler_82c6c {
    u32 write_504d98;
    u32 value_504d98;
    u32 write_504d80;
    u32 value_504d80;
};

struct recovered_state_scheduler_handler_82c6c
recovered_state_scheduler_handler_82c6c(u32 object_state,
                                        int32_t value_504dc0,
                                        u32 control_504e28)
{
    struct recovered_state_scheduler_handler_82c6c out = {0U, 0U, 0U, 0U};

    if (object_state != 4U) {
        out.write_504d98 = 1U;
        out.value_504d98 = 2U;
        return out;
    }
    if (value_504dc0 <= (int32_t)0x78000) {
        out.write_504d80 = 1U;
        out.value_504d80 = 8U;
        return out;
    }
    out.write_504d98 = 1U;
    out.value_504d98 = 3U;
    out.write_504d80 = 1U;
    out.value_504d80 = control_504e28 == 1U ? 28U : 5U;
    return out;
}
