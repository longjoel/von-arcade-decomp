/* Status-scene arm 4 recovered from i960 0xe8e44-0xe8fac. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 feature_flags;
    recovered_u32 object_tag[3];
    recovered_u32 admitted;
    recovered_u32 packet[5];
    recovered_u32 packet_count;
    recovered_u32 dispatch_target;
    recovered_u32 transform_0;
    recovered_u32 transform_1[3];
    recovered_u32 transform_2;
    recovered_u32 completion_word;
    recovered_u32 cleanup_target;
    recovered_u32 return_target;
} recovered_geometry_status_scene_arm4_result_e8e44;

recovered_geometry_status_scene_arm4_result_e8e44
recovered_geometry_status_scene_arm4_e8e44(recovered_u32 feature_flags,
                                            recovered_u32 object_tag_0,
                                            recovered_u32 object_tag_1,
                                            recovered_u32 object_tag_2)
{
    recovered_geometry_status_scene_arm4_result_e8e44 result;

    result.feature_flags = feature_flags;
    result.object_tag[0] = object_tag_0 & 0xffU;
    result.object_tag[1] = object_tag_1 & 0xffU;
    result.object_tag[2] = object_tag_2 & 0xffU;
    result.admitted = (feature_flags & (1U << 3)) != 0U;
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
    result.completion_word = 6U;
    result.cleanup_target = 0x000e8facU;
    result.return_target = 0x000e8fe0U;
    return result;
}
