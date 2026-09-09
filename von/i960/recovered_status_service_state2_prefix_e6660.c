/* State-2 status service prefix recovered from i960 0xe6660-0xe66b4. */
#include "recovered_common.h"

typedef struct {
    int32_t timer_value;
    int32_t remainder;
    recovered_u32 route;
    recovered_u32 target;
    recovered_u32 helper_target;
    recovered_u32 status_504d2c;
    recovered_u32 status_504d24;
    recovered_u32 status_504d2e;
    recovered_u32 device_bit_address;
    recovered_u32 device_bit;
    recovered_u32 continuation;
    recovered_u32 modulus;
} recovered_status_service_state2_result_e6660;

enum recovered_status_service_state2_route_e6660 {
    RECOVERED_STATUS_STATE2_EARLY_RETURN = 0,
    RECOVERED_STATUS_STATE2_SPECIAL_438 = 1,
    RECOVERED_STATUS_STATE2_GENERAL = 2
};

recovered_status_service_state2_result_e6660
recovered_status_service_state2_prefix_e6660(int32_t timer_value)
{
    recovered_status_service_state2_result_e6660 result;

    result.timer_value = timer_value;
    result.remainder = timer_value % 0x870;
    result.route = RECOVERED_STATUS_STATE2_GENERAL;
    result.target = 0x000e66b4U;
    result.helper_target = 0;
    result.status_504d2c = 0;
    result.status_504d24 = 0;
    result.status_504d2e = 0;
    result.device_bit_address = 0;
    result.device_bit = 0;
    result.continuation = 0;
    result.modulus = 0x870U;

    if (result.remainder <= 0x437) {
        result.route = RECOVERED_STATUS_STATE2_EARLY_RETURN;
        result.target = 0x000e6678U;
    } else if (result.remainder == 0x438) {
        result.route = RECOVERED_STATUS_STATE2_SPECIAL_438;
        result.target = 0x000e6680U;
        result.helper_target = 0x0001c618U;
        result.status_504d2c = 0xc000U;
        result.status_504d24 = 0x200U;
        result.status_504d2e = 0x8000U;
        result.device_bit_address = 0x0100a000U;
        result.device_bit = 9U;
        result.continuation = 0x000e6c50U;
    }
    return result;
}
