/* State-1 transition gateway prefix recovered from i960 0xe61c0-0xe6208. */
#include <stdint.h>

typedef uint32_t recovered_u32;

enum recovered_status_transition_variant_route_e61c0 {
    RECOVERED_STATUS_VARIANT_EARLY_RETURN = 0,
    RECOVERED_STATUS_VARIANT_SPECIAL_438 = 1,
    RECOVERED_STATUS_VARIANT_GENERAL = 2
};

typedef struct {
    int32_t timer_value;
    int32_t remainder;
    recovered_u32 route;
    recovered_u32 target;
    recovered_u32 continuation;
    recovered_u32 modulus;
} recovered_status_transition_variant_result_e61c0;

recovered_status_transition_variant_result_e61c0
recovered_status_transition_variant_prefix_e61c0(int32_t timer_value)
{
    recovered_status_transition_variant_result_e61c0 result;

    result.timer_value = timer_value;
    result.remainder = timer_value % 0x870;
    result.modulus = 0x870U;
    result.continuation = 0U;
    if (result.remainder <= 0x437) {
        result.route = RECOVERED_STATUS_VARIANT_EARLY_RETURN;
        result.target = 0x000e61d0U;
    } else if (result.remainder == 0x438) {
        result.route = RECOVERED_STATUS_VARIANT_SPECIAL_438;
        result.target = 0x000e61dcU;
        result.continuation = 0x000e6410U;
    } else {
        result.route = RECOVERED_STATUS_VARIANT_GENERAL;
        result.target = 0x000e6208U;
    }
    return result;
}
