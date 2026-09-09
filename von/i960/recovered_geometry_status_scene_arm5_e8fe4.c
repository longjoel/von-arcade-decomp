/* Status-scene arm 5 recovered from i960 0xe8fe4-0xe9138. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 object_tag[3];
    recovered_u32 packet[5];
    recovered_u32 packet_count;
    recovered_u32 dispatch_target;
    recovered_u32 transform_0;
    recovered_u32 transform_1[3];
    recovered_u32 transform_2;
    recovered_u32 completion_target;
    recovered_u32 completion_word;
    recovered_u32 return_target;
} recovered_geometry_status_scene_arm5_result_e8fe4;

recovered_geometry_status_scene_arm5_result_e8fe4
recovered_geometry_status_scene_arm5_e8fe4(recovered_u32 object_tag_0,
                                            recovered_u32 object_tag_1,
                                            recovered_u32 object_tag_2)
{
    recovered_geometry_status_scene_arm5_result_e8fe4 result;

    result.object_tag[0] = object_tag_0 & 0xffU;
    result.object_tag[1] = object_tag_1 & 0xffU;
    result.object_tag[2] = object_tag_2 & 0xffU;
    result.packet[0] = 5U;
    result.packet[1] = 19U;
    result.packet[2] = 0x41400000U;
    result.packet[3] = 0x41400000U;
    result.packet[4] = RECOVERED_FLOAT_ONE;
    result.packet_count = 5U;
    result.dispatch_target = 0x000e7390U;
    result.transform_0 = 0x49c980U;
    result.transform_1[0] = 0xc0c00000U;
    result.transform_1[1] = 0U;
    result.transform_1[2] = 0x40c00000U;
    result.transform_2 = 0xc0900000U;
    result.completion_target = 0x000e8e34U;
    result.completion_word = 6U;
    result.return_target = 0x000e9138U;
    return result;
}
