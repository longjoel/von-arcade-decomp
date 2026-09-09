/* State-2 remainder-0x674 second-half path recovered from i960 0xe6968-0xe6c50. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 remainder;
    recovered_u32 route;
    recovered_u32 status_504d2c;
    recovered_u32 status_504d24;
    recovered_u32 status_504d2e;
    recovered_u32 device_bit_address;
    recovered_u32 device_bit;
    recovered_u32 source_base;
    recovered_u32 source_stride;
    recovered_u32 source_count;
    recovered_u32 frame_record_stride;
    recovered_u32 first_rendered_row;
    recovered_u32 rendered_row_count;
    recovered_u32 first_frame_offset;
    recovered_u32 first_text_column;
    recovered_u32 text_column_stride;
    recovered_u32 renderer_target;
    recovered_u32 profile_dispatch_target;
    recovered_u32 profile_call_count;
    recovered_u32 frame_selector_offsets[4];
    recovered_u32 renderer_arg0[4];
    recovered_u32 renderer_arg1[4];
    recovered_u32 continuation;
} recovered_status_service_state2_second_half_result_e6968;

enum recovered_status_service_state2_second_half_route_e6968 {
    RECOVERED_STATUS_STATE2_SECOND_HALF_FALLTHROUGH = 0,
    RECOVERED_STATUS_STATE2_SECOND_HALF_RENDER = 1
};

recovered_status_service_state2_second_half_result_e6968
recovered_status_service_state2_second_half_e6968(recovered_u32 remainder)
{
    recovered_status_service_state2_second_half_result_e6968 result = {
        remainder, RECOVERED_STATUS_STATE2_SECOND_HALF_FALLTHROUGH,
        0, 0, 0, 0, 0,
        0x01d000a4U, 16U, 10U, 12U,
        0, 0, 0, 19U, 3U,
        0x0001d880U, 0x000e6500U, 4U,
        {0x70U, 0x7cU, 0x88U, 0x94U},
        {2U, 31U, 2U, 31U},
        {13U, 16U, 25U, 28U},
        0x000e6c50U
    };

    if (remainder != 0x674U)
        return result;

    result.route = RECOVERED_STATUS_STATE2_SECOND_HALF_RENDER;
    result.status_504d2c = 0xc000U;
    result.status_504d24 = 0x200U;
    result.status_504d2e = 0x8000U;
    result.device_bit_address = 0x0100a000U;
    result.device_bit = 9U;
    result.first_rendered_row = 4U;
    result.rendered_row_count = 4U;
    result.first_frame_offset = 0x30U;
    return result;
}
