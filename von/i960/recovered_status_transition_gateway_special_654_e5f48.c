/* Exact-0x654 gateway arm recovered from i960 0xe5f48-0xe5f88. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 status_504d2c;
    recovered_u32 status_504d2e;
    recovered_u32 status_504d24;
    recovered_u32 device_bit_address;
    recovered_u32 device_bit;
    recovered_u32 renderer_arg0;
    recovered_u32 renderer_arg1;
    recovered_u32 helper_target;
    recovered_u32 continuation;
} recovered_status_transition_gateway_special_654_result_e5f48;

void recovered_status_transition_gateway_special_654_e5f48(
    recovered_status_transition_gateway_special_654_result_e5f48 *result)
{
    result->status_504d2c = 0xc000U;
    result->status_504d2e = 0x8000U;
    result->status_504d24 = 0x200U;
    result->device_bit_address = 0x0100a000U;
    result->device_bit = 9U;
    result->renderer_arg0 = 13U;
    result->renderer_arg1 = 12U;
    result->helper_target = 0x0001cac8U;
    result->continuation = 0x000e5f88U;
}
