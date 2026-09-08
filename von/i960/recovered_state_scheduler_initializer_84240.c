/* Scheduler initializer recovered from i960 0x84240-0x84290. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_scheduler_initializer_84240 {
    u32 callback_target;
    u32 callback_g14;
    u32 value_504e1c;
    u32 value_504d80;
    u32 value_504d8c;
    u32 value_504d90;
    u32 value_504d9c;
};

struct recovered_state_scheduler_initializer_84240
recovered_state_scheduler_initializer_84240(void)
{
    struct recovered_state_scheduler_initializer_84240 out = {
        0x84290U, 0U, 1U, 43U, 0U, 15U, 7U
    };
    return out;
}
