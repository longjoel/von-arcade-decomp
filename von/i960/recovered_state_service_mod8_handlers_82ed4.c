/* Modulo-8 service handlers recovered from i960 0x82ed4-0x82f6c. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_state_service_mod8_route {
    RECOVERED_SERVICE_MOD8_SHARED_FALLBACK = 0,
    RECOVERED_SERVICE_MOD8_VALUE_3 = 1,
    RECOVERED_SERVICE_MOD8_VALUE_4 = 2,
    RECOVERED_SERVICE_MOD8_VALUE_6 = 3
};

struct recovered_state_service_mod8_plan {
    enum recovered_state_service_mod8_route route;
    u32 downstream_value;
};

struct recovered_state_service_mod8_plan
recovered_state_service_mod8_handler(u32 entry, u32 remainder_8,
                                     u32 object_state)
{
    struct recovered_state_service_mod8_plan out = {
        RECOVERED_SERVICE_MOD8_SHARED_FALLBACK, 0U
    };

    if (entry == 0x82ed4U) {
        if (remainder_8 < 3U && object_state == 3U) {
            out.route = RECOVERED_SERVICE_MOD8_VALUE_3;
            out.downstream_value = 3U;
        } else if (remainder_8 == 6U) {
            out.route = RECOVERED_SERVICE_MOD8_VALUE_4;
            out.downstream_value = 4U;
        }
    } else if (entry == 0x82f10U) {
        if ((remainder_8 == 4U || remainder_8 == 5U)
            && object_state == 3U) {
            out.route = RECOVERED_SERVICE_MOD8_VALUE_3;
            out.downstream_value = 3U;
        } else if (remainder_8 == 7U && object_state == 3U) {
            out.route = RECOVERED_SERVICE_MOD8_VALUE_6;
            out.downstream_value = 6U;
        }
    }
    return out;
}
