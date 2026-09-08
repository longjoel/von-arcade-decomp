/* Service handler recovered from i960 0x82ea0-0x82ed4. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_state_service_handler_82ea0_route {
    RECOVERED_SERVICE_82EA0_SHARED_FALLBACK = 0,
    RECOVERED_SERVICE_82EA0_VALUE_3 = 1,
    RECOVERED_SERVICE_82EA0_VALUE_6 = 2
};

struct recovered_state_service_handler_82ea0 {
    enum recovered_state_service_handler_82ea0_route route;
    u32 downstream_value;
};

struct recovered_state_service_handler_82ea0
recovered_state_service_handler_82ea0(u32 random_remainder_6,
                                      u32 object_state)
{
    struct recovered_state_service_handler_82ea0 out = {
        RECOVERED_SERVICE_82EA0_SHARED_FALLBACK, 0U
    };

    if (object_state != 3U)
        return out;
    if (random_remainder_6 == 4U) {
        out.route = RECOVERED_SERVICE_82EA0_VALUE_3;
        out.downstream_value = 3U;
    } else if (random_remainder_6 == 5U) {
        out.route = RECOVERED_SERVICE_82EA0_VALUE_6;
        out.downstream_value = 6U;
    }
    return out;
}
