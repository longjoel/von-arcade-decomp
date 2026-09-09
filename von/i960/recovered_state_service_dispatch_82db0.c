/* State-service dispatcher recovered from i960 0x82db0-0x82dd0. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_state_service_dispatch_82db0_route {
    RECOVERED_STATE_SERVICE_TABLE = 0,
    RECOVERED_STATE_SERVICE_HIGH_STATE = 1
};

struct recovered_state_service_dispatch_82db0 {
    enum recovered_state_service_dispatch_82db0_route route;
    u32 target;
    u32 handler_value_74;
    u32 handler_object_pointer;
};

static const u32 targets[9] = {
    0x82df8U, 0x82e0cU, 0x82e40U, 0x82e64U, 0x82ea0U,
    0x82ed4U, 0x82f10U, 0x82f6cU, 0x82f84U
};

struct recovered_state_service_dispatch_82db0
recovered_state_service_dispatch_82db0(u32 object_state, u32 object_value_74,
                                        u32 object_pointer)
{
    struct recovered_state_service_dispatch_82db0 out = {
        RECOVERED_STATE_SERVICE_HIGH_STATE, 0x82f90U, object_value_74,
        object_pointer
    };

    if (object_state <= 8U) {
        out.route = RECOVERED_STATE_SERVICE_TABLE;
        out.target = targets[object_state];
    }
    return out;
}
