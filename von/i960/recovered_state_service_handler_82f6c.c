/* Service handler recovered from i960 0x82f6c-0x82fac. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_service_handler_82f6c {
    u32 accepted;
    u32 downstream_value;
};

struct recovered_state_service_handler_82f6c
recovered_state_service_handler_82f6c(u32 random_remainder_5,
                                      u32 object_state)
{
    struct recovered_state_service_handler_82f6c out = {0U, 0U};

    if (random_remainder_5 == 4U && object_state == 3U) {
        out.accepted = 1U;
        out.downstream_value = 2U;
    }
    return out;
}
