/* Shared service handler write prefix recovered from i960 0x82fdc-0x830c0. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_service_shared_handler_prefix_82fdc {
    u32 write_504d94;
    u32 value_504d94;
    u32 write_504d98;
    u32 value_504d98;
    u32 write_504db8;
    u32 value_504db8;
    u32 calls_79050;
    u32 calls_79d60;
};

struct recovered_state_service_shared_handler_prefix_82fdc
recovered_state_service_shared_handler_prefix_82fdc(u32 selector, u32 g14)
{
    struct recovered_state_service_shared_handler_prefix_82fdc out = {
        0U, 0U, 0U, 0U, 0U, 0U, 0U, 0U
    };

    switch (selector) {
    case 0U:
        out.write_504d94 = 1U; out.value_504d94 = 5U;
        out.write_504db8 = 1U; out.value_504db8 = 30U;
        out.calls_79050 = 1U;
        break;
    case 1U:
        out.write_504d94 = 1U; out.value_504d94 = 6U;
        out.write_504db8 = 1U; out.value_504db8 = 30U;
        out.calls_79050 = 1U;
        break;
    case 2U:
        out.write_504d94 = 1U; out.value_504d94 = 2U;
        out.write_504db8 = 1U; out.value_504db8 = 30U;
        out.calls_79050 = 1U;
        break;
    case 3U:
        out.write_504d94 = 1U; out.value_504d94 = 3U;
        out.write_504db8 = 1U; out.value_504db8 = 30U;
        out.calls_79050 = 1U;
        break;
    case 4U:
        out.write_504d98 = 1U; out.value_504d98 = 1U;
        out.write_504db8 = 1U; out.value_504db8 = 20U;
        out.write_504d94 = 1U; out.value_504d94 = g14;
        break;
    case 5U:
        out.write_504d98 = 1U; out.value_504d98 = 2U;
        out.write_504db8 = 1U; out.value_504db8 = 20U;
        out.write_504d94 = 1U; out.value_504d94 = g14;
        break;
    case 6U:
        out.write_504d98 = 1U; out.value_504d98 = 3U;
        out.write_504db8 = 1U; out.value_504db8 = 20U;
        out.write_504d94 = 1U; out.value_504d94 = g14;
        break;
    case 7U:
        out.write_504d94 = 1U; out.value_504d94 = 7U;
        out.write_504db8 = 1U; out.value_504db8 = 30U;
        out.calls_79d60 = 1U;
        break;
    default:
        out.write_504d98 = 1U; out.value_504d98 = 1U;
        out.write_504db8 = 1U; out.value_504db8 = 10U;
        out.write_504d94 = 1U; out.value_504d94 = g14;
        break;
    }
    return out;
}
