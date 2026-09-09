/* State-1 exact-0x438 arm recovered from i960 0xe61dc-0xe6208. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 helper_target;
    recovered_u32 status_504d2c;
    recovered_u32 status_504d2e;
    recovered_u32 device_bit_address;
    recovered_u32 device_bit;
    recovered_u32 continuation;
} recovered_status_transition_variant_special_438_result_e61dc;

void recovered_status_transition_variant_special_438_e61dc(
    recovered_status_transition_variant_special_438_result_e61dc *result)
{
    result->helper_target = 0x0001c618U;
    result->status_504d2c = 0xc000U;
    result->status_504d2e = 0x8000U;
    result->device_bit_address = 0x0100a000U;
    result->device_bit = 9U;
    result->continuation = 0x000e6410U;
}
