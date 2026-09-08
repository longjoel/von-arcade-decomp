/* Scheduler-side wrapper recovered from i960 0x842d0-0x8432c. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_wrapper_842d0 {
    u32 skipped;
    u32 call_84330;
    u32 call_85c00;
    u32 call_848d0;
    u32 call_84b10;
    u32 call_858f0;
    u32 call_85b00;
};

struct recovered_scheduler_wrapper_842d0
recovered_scheduler_wrapper_842d0(u32 value_504e50, u32 value_5024e8)
{
    struct recovered_scheduler_wrapper_842d0 out = {0U, 0U, 0U, 0U, 0U, 0U, 0U};

    if ((value_504e50 & 1U) != 0U) {
        out.skipped = 1U;
        return out;
    }
    out.call_84330 = 1U;
    out.call_85c00 = 1U;
    out.call_848d0 = 1U;
    out.call_84b10 = 1U;
    out.call_858f0 = 1U;
    out.call_85b00 = (value_5024e8 & 0xffU) == 0U;
    return out;
}
