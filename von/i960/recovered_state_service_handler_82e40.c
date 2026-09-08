/* Service handler recovered from i960 0x82e40-0x82e60. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_state_service_handler_82e40_route {
    RECOVERED_SERVICE_82E40_SHARED_FALLBACK = 0,
    RECOVERED_SERVICE_82E40_VALUE_2 = 1,
    RECOVERED_SERVICE_82E40_VALUE_5 = 2
};

struct recovered_state_service_handler_82e40 {
    enum recovered_state_service_handler_82e40_route route;
    u32 downstream_value;
};

struct recovered_state_service_handler_82e40
recovered_state_service_handler_82e40(u32 random_remainder_5,
                                      u32 object_state)
{
    struct recovered_state_service_handler_82e40 out = {
        RECOVERED_SERVICE_82E40_SHARED_FALLBACK, 0U
    };

    if (random_remainder_5 != 4U)
        return out;
    if (object_state == 3U) {
        out.route = RECOVERED_SERVICE_82E40_VALUE_2;
        out.downstream_value = 2U;
    } else {
        out.route = RECOVERED_SERVICE_82E40_VALUE_5;
        out.downstream_value = 5U;
    }
    return out;
}
