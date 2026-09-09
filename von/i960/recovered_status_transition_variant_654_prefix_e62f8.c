/* State-1 remainder-0x654 renderer prefix recovered from i960 0xe62f8-0xe6410. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 remainder;
    recovered_u32 route;
    recovered_u32 status_504d2c;
    recovered_u32 status_504d2e;
    recovered_u32 status_504d24;
    recovered_u32 device_bit_address;
    recovered_u32 device_bit;
    recovered_u32 renderer_arg0;
    recovered_u32 renderer_arg1;
    recovered_u32 helper_target;
    recovered_u32 record_base;
    recovered_u32 first_record_offset;
    recovered_u32 record_index_offset;
    recovered_u32 record_stride;
    recovered_u32 record_count;
    recovered_u32 first_text_column;
    recovered_u32 text_column_stride;
    recovered_u32 continuation;
} recovered_status_transition_variant_654_result_e62f8;

enum recovered_status_transition_variant_654_route_e62f8 {
    RECOVERED_STATUS_VARIANT_654_FALLTHROUGH = 0,
    RECOVERED_STATUS_VARIANT_654_RENDER = 1
};

recovered_status_transition_variant_654_result_e62f8
recovered_status_transition_variant_654_prefix_e62f8(recovered_u32 remainder)
{
    recovered_status_transition_variant_654_result_e62f8 result;

    result.remainder = remainder;
    result.route = RECOVERED_STATUS_VARIANT_654_FALLTHROUGH;
    result.status_504d2c = 0;
    result.status_504d2e = 0;
    result.status_504d24 = 0;
    result.device_bit_address = 0;
    result.device_bit = 0;
    result.renderer_arg0 = 0;
    result.renderer_arg1 = 0;
    result.helper_target = 0;
    result.record_base = 0;
    result.first_record_offset = 0;
    result.record_index_offset = 0;
    result.record_stride = 0;
    result.record_count = 0;
    result.first_text_column = 0;
    result.text_column_stride = 0;
    result.continuation = 0x000e6410U;

    if (remainder != 0x654U)
        return result;

    result.route = RECOVERED_STATUS_VARIANT_654_RENDER;
    result.status_504d2c = 0xc000U;
    result.status_504d2e = 0x8000U;
    result.status_504d24 = 0x200U;
    result.device_bit_address = 0x0100a000U;
    result.device_bit = 9U;
    result.renderer_arg0 = 13U;
    result.renderer_arg1 = 12U;
    result.helper_target = 0x0001cac8U;
    result.record_base = 0x00578460U;
    result.first_record_offset = 0x3cU;
    result.record_index_offset = 31U;
    result.record_stride = 12U;
    result.record_count = 5U;
    result.first_text_column = 19U;
    result.text_column_stride = 3U;
    return result;
}
