/* Constant scheduler handlers recovered from i960 0x82cc0-0x82ce8. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_scheduler_constant_handler_82cc0 {
    u32 handled;
    u32 value_504d98;
};

struct recovered_state_scheduler_constant_handler_82cc0
recovered_state_scheduler_constant_handler_82cc0(u32 entry)
{
    struct recovered_state_scheduler_constant_handler_82cc0 out = {0U, 0U};

    switch (entry) {
    case 0x82cc0U:
        out.handled = 1U;
        out.value_504d98 = 3U;
        break;
    case 0x82cc8U:
        out.handled = 1U;
        out.value_504d98 = 1U;
        break;
    case 0x82cd0U:
        out.handled = 1U;
        out.value_504d98 = 13U;
        break;
    case 0x82cd8U:
        out.handled = 1U;
        out.value_504d98 = 14U;
        break;
    case 0x82ce0U:
        out.handled = 1U;
        out.value_504d98 = 15U;
        break;
    default:
        break;
    }
    return out;
}
