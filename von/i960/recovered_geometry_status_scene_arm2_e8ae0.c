/* Status-scene arm 2 recovered from i960 0xe8ae0-0xe8c58. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 feature_flags;
    recovered_u32 scene_count;
    recovered_u32 fixed_object_tag_0;
    recovered_u32 fixed_object_tag_1;
    recovered_u32 indexed_object_tag;
    recovered_u32 third_call_admitted;
    recovered_u32 packet[5];
    recovered_u32 packet_count;
    recovered_u32 dispatch_target;
    recovered_u32 common_transform_0;
    recovered_u32 first_transform_1;
    recovered_u32 common_transform_2;
    recovered_u32 third_transform_1;
    recovered_u32 completion_word;
    recovered_u32 return_target;
} recovered_geometry_status_scene_arm2_result_e8ae0;

recovered_geometry_status_scene_arm2_result_e8ae0
recovered_geometry_status_scene_arm2_e8ae0(recovered_u32 feature_flags,
                                            recovered_u32 scene_count,
                                            recovered_u32 fixed_object_tag_0,
                                            recovered_u32 fixed_object_tag_1,
                                            recovered_u32 indexed_object_tag)
{
    recovered_geometry_status_scene_arm2_result_e8ae0 result;

    result.feature_flags = feature_flags;
    result.scene_count = scene_count;
    result.fixed_object_tag_0 = fixed_object_tag_0 & 0xffU;
    result.fixed_object_tag_1 = fixed_object_tag_1 & 0xffU;
    result.indexed_object_tag = indexed_object_tag & 0xffU;
    result.third_call_admitted = (feature_flags & (1U << 3)) != 0U;
    result.packet[0] = 5U;
    result.packet[1] = 19U;
    result.packet[2] = 0x41400000U;
    result.packet[3] = 0x41400000U;
    result.packet[4] = RECOVERED_FLOAT_ONE;
    result.packet_count = 5U;
    result.dispatch_target = 0x000e7390U;
    result.common_transform_0 = 0x49c980U;
    result.first_transform_1 = 0xc0c00000U;
    result.common_transform_2 = 0xc0900000U;
    result.third_transform_1 = 0x40c00000U;
    result.completion_word = 6U;
    result.return_target = 0x000e8c58U;
    return result;
}
