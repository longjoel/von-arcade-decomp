/* Object packet response split recovered from i960 0xe7490-0xe7560. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 computed_offset;
    recovered_u32 control_word;
    recovered_u32 control_flag;
    recovered_u32 fifo_readback;
    recovered_u32 common_fifo_words[2];
    recovered_u32 fifo_address;
    recovered_u32 control_read_address;
    recovered_u32 control_write_address;
    recovered_u32 control_write_value;
    recovered_u32 route;
    recovered_u32 fallback_asset0;
    recovered_u32 fallback_asset1;
    recovered_u32 fallback_asset2;
    recovered_u32 fallback_status;
    recovered_u32 fallback_status_address;
    recovered_u32 queued_status;
    recovered_u32 queued_control;
    recovered_u32 queued_parameter_address;
    recovered_u32 queued_parameter;
    recovered_u32 queued_block_address;
    recovered_u32 return_target;
} recovered_geometry_object_packet_response_result_e7490;

enum recovered_geometry_object_packet_response_route_e7490 {
    RECOVERED_GEOMETRY_OBJECT_PACKET_FALLBACK = 0,
    RECOVERED_GEOMETRY_OBJECT_PACKET_QUEUED = 1
};

recovered_geometry_object_packet_response_result_e7490
recovered_geometry_object_packet_response_e7490(recovered_u32 computed_offset,
                                                recovered_u32 control_word,
                                                recovered_u32 control_flag,
                                                recovered_u32 fifo_readback,
                                                recovered_u32 queued_parameter)
{
    recovered_geometry_object_packet_response_result_e7490 result = {
        computed_offset, control_word, control_flag, fifo_readback,
        {computed_offset + 27U, control_word},
        0x00884000U, 0x00802008U, 0x00801008U, control_word + 0x34U,
        RECOVERED_GEOMETRY_OBJECT_PACKET_FALLBACK,
        0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0x000e7514U
    };

    if (control_flag == 0U) {
        result.fallback_asset0 = 0x0049317cU;
        result.fallback_asset1 = 0x004931acU;
        result.fallback_asset2 = 0x00900514U;
        result.fallback_status = 0x101U;
        result.fallback_status_address = 0x00800010U;
        return result;
    }

    result.route = RECOVERED_GEOMETRY_OBJECT_PACKET_QUEUED;
    result.queued_status = 0x101U;
    result.queued_control = 0x00400020U;
    result.queued_parameter_address = 0x00804004U;
    result.queued_parameter = queued_parameter;
    result.queued_block_address = 0x00804000U;
    result.return_target = 0x000e755cU;
    return result;
}
