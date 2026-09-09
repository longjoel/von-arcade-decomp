/* State-1 remainder-0x439 renderer prefix recovered from i960 0xe6208-0xe62f8. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 remainder;
    recovered_u32 route;
    recovered_u32 helper_target;
    recovered_u32 renderer_target;
    recovered_u32 record_base;
    recovered_u32 record_stride;
    recovered_u32 record_count;
    recovered_u32 first_text_column;
    recovered_u32 text_column_stride;
    recovered_u32 continuation;
} recovered_status_transition_variant_439_result_e6208;

enum recovered_status_transition_variant_439_route_e6208 {
    RECOVERED_STATUS_VARIANT_439_FALLTHROUGH = 0,
    RECOVERED_STATUS_VARIANT_439_RENDER = 1
};

recovered_status_transition_variant_439_result_e6208
recovered_status_transition_variant_439_prefix_e6208(recovered_u32 remainder)
{
    recovered_status_transition_variant_439_result_e6208 result;

    result.remainder = remainder;
    result.route = RECOVERED_STATUS_VARIANT_439_FALLTHROUGH;
    result.helper_target = 0;
    result.renderer_target = 0;
    result.record_base = 0;
    result.record_stride = 0;
    result.record_count = 0;
    result.first_text_column = 0;
    result.text_column_stride = 0;
    result.continuation = 0x000e6410U;

    if (remainder != 0x439U)
        return result;

    result.route = RECOVERED_STATUS_VARIANT_439_RENDER;
    result.helper_target = 0x0001cac8U;
    result.renderer_target = 0x0001d880U;
    result.record_base = 0x00578460U;
    result.record_stride = 12U;
    result.record_count = 5U;
    result.first_text_column = 19U;
    result.text_column_stride = 3U;
    return result;
}
