/* Ratio-table handlers recovered from i960 0x833dc-0x83428. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_scheduler_ratio_handler_833dc {
    u32 handled;
    u32 status_write;
    u32 value_504d80;
    u32 calls_79d60;
};

struct recovered_state_scheduler_ratio_handler_833dc
recovered_state_scheduler_ratio_handler_833dc(u32 entry)
{
    struct recovered_state_scheduler_ratio_handler_833dc out = {
        0U, 0U, 0U, 0U
    };

    switch (entry) {
    case 0x833dcU:
        out.handled = 1U;
        out.calls_79d60 = 1U;
        break;
    case 0x833e8U:
    case 0x833f8U:
        out.handled = 1U;
        out.status_write = 1U;
        out.value_504d80 = 28U;
        break;
    case 0x83408U:
        out.handled = 1U;
        out.status_write = 1U;
        out.value_504d80 = 26U;
        break;
    case 0x83418U:
        out.handled = 1U;
        out.status_write = 1U;
        out.value_504d80 = 21U;
        break;
    default:
        break;
    }
    return out;
}
