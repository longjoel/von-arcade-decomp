/* Exact-0x439 gateway gate recovered from i960 0xe5de8-0xe5df0. */
#include <stdint.h>

typedef uint32_t recovered_u32;

enum recovered_status_transition_gateway_439_route_e5de8 {
    RECOVERED_STATUS_TRANSITION_439_RENDER = 0,
    RECOVERED_STATUS_TRANSITION_OTHER_GENERAL = 1
};

typedef struct {
    int32_t remainder;
    recovered_u32 route;
    recovered_u32 target;
    recovered_u32 tested_value;
} recovered_status_transition_gateway_439_result_e5de8;

recovered_status_transition_gateway_439_result_e5de8
recovered_status_transition_gateway_439_gate_e5de8(int32_t remainder)
{
    recovered_status_transition_gateway_439_result_e5de8 result = {
        remainder, RECOVERED_STATUS_TRANSITION_OTHER_GENERAL,
        0x000e5f48U, 0x439U
    };

    if (remainder == 0x439) {
        result.route = RECOVERED_STATUS_TRANSITION_439_RENDER;
        result.target = 0x000e5df0U;
    }
    return result;
}
