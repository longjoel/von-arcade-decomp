/* Transition gateway prefix recovered from i960 0xe5da0-0xe5de8. */
#include <stdint.h>

typedef uint32_t recovered_u32;

enum recovered_status_transition_gateway_route_e5da0 {
    RECOVERED_STATUS_TRANSITION_EARLY_RETURN = 0,
    RECOVERED_STATUS_TRANSITION_SPECIAL_438 = 1,
    RECOVERED_STATUS_TRANSITION_GENERAL = 2
};

typedef struct {
    int32_t timer_value;
    int32_t remainder;
    recovered_u32 route;
    recovered_u32 target;
    recovered_u32 modulus;
    recovered_u32 special_remainder;
    recovered_u32 lower_bound;
} recovered_status_transition_gateway_result_e5da0;

/*
 * remi uses the signed caller timer.  The literal-first greater-than check
 * admits only remainders above 0x437; exactly 0x438 takes the special packet
 * arm, while the other admitted values continue at 0xe5de8.
 */
recovered_status_transition_gateway_result_e5da0
recovered_status_transition_gateway_prefix_e5da0(int32_t timer_value)
{
    recovered_status_transition_gateway_result_e5da0 result;

    result.timer_value = timer_value;
    result.remainder = timer_value % 0x870;
    result.modulus = 0x870U;
    result.special_remainder = 0x438U;
    result.lower_bound = 0x437U;
    if (result.remainder <= 0x437) {
        result.route = RECOVERED_STATUS_TRANSITION_EARLY_RETURN;
        result.target = 0x000e5db0U;
    } else if (result.remainder == 0x438) {
        result.route = RECOVERED_STATUS_TRANSITION_SPECIAL_438;
        result.target = 0x000e5dbcU;
    } else {
        result.route = RECOVERED_STATUS_TRANSITION_GENERAL;
        result.target = 0x000e5de8U;
    }
    return result;
}
