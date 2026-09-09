/* Fallback object packet path recovered from i960 0xe7874-0xe78a8. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 saved_base;
    recovered_u32 computed_offset;
    recovered_u32 coordinate0;
    recovered_u32 coordinate1;
    recovered_u32 control_flag;
    recovered_u32 fifo_readback;
    recovered_u32 packet_words[4];
    recovered_u32 suffix_word_count;
    recovered_u32 suffix_words[5];
    recovered_u32 control_read_address;
    recovered_u32 control_write_address;
    recovered_u32 fallback_asset0;
    recovered_u32 fallback_asset1;
    recovered_u32 fallback_asset2;
    recovered_u32 fallback_status;
    recovered_u32 queued_status;
    recovered_u32 queued_control;
    recovered_u32 queued_descriptor;
    recovered_u32 queued_parameter_address;
    recovered_u32 queued_block_address;
    recovered_u32 fallback_return_target;
    recovered_u32 queued_return_target;
} recovered_geometry_object_fallback_packet_result_e7874;

recovered_geometry_object_fallback_packet_result_e7874
recovered_geometry_object_fallback_packet_e7874(recovered_u32 saved_base,
                                                recovered_u32 computed_offset,
                                                recovered_u32 coordinate0,
                                                recovered_u32 coordinate1,
                                                recovered_u32 control_flag,
                                                recovered_u32 fifo_readback)
{
    recovered_geometry_object_fallback_packet_result_e7874 result = {
        saved_base, computed_offset, coordinate0, coordinate1,
        control_flag, fifo_readback, {18U, 0U, 0U, 0U}, 0U,
        {0U, 0U, 0U, 0U, 0U},
        0x00802008U, 0x00801008U,
        0, 0, 0, 0, 0, 0, 0, 0, 0,
        0x000e77f4U, 0x000e784cU
    };

    result.packet_words[1] = saved_base + computed_offset;
    result.packet_words[2] = coordinate0;
    result.packet_words[3] = coordinate1;
    if (control_flag == 0U) {
        result.suffix_word_count = 5U;
        result.suffix_words[0] = 19U;
        result.suffix_words[1] = 0x3f800000U;
        result.suffix_words[2] = 0x3f800000U;
        result.suffix_words[3] = 0x41200000U;
        result.suffix_words[4] = computed_offset + 27U;
    }
    if (control_flag == 0U) {
        result.fallback_asset0 = 0x0049353cU;
        result.fallback_asset1 = 0x00493744U;
        result.fallback_asset2 = 0x009009b6U;
        result.fallback_status = 0x101U;
        return result;
    }
    result.queued_status = 0x101U;
    result.queued_control = 0x00400020U;
    result.queued_descriptor = 0x008fe654U;
    result.queued_parameter_address = 0x00804004U;
    result.queued_block_address = 0x00804000U;
    return result;
}
