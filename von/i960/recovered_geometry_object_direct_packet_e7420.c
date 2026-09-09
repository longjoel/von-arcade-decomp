/* Direct object packet prefix recovered from i960 0xe7420-0xe7454. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 saved_base;
    recovered_u32 computed_offset;
    recovered_u32 coordinate0;
    recovered_u32 coordinate1;
    recovered_u32 packet_words[4];
    recovered_u32 fifo_address;
    recovered_u32 next_target;
} recovered_geometry_object_direct_packet_result_e7420;

recovered_geometry_object_direct_packet_result_e7420
recovered_geometry_object_direct_packet_e7420(recovered_u32 saved_base,
                                              recovered_u32 computed_offset,
                                              recovered_u32 coordinate0,
                                              recovered_u32 coordinate1)
{
    recovered_geometry_object_direct_packet_result_e7420 result = {
        saved_base, computed_offset, coordinate0, coordinate1,
        {18U, 0U, 0U, 0U}, 0x00884000U, 0x000e7454U
    };

    result.packet_words[1] = saved_base + computed_offset;
    result.packet_words[2] = coordinate0;
    result.packet_words[3] = coordinate1;
    return result;
}
