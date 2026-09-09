/* Status-scene arm 1 recovered from i960 0xe89d4-0xe8adc. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 feature_flags;
    recovered_u32 scene_count;
    recovered_u32 fixed_object_tag;
    recovered_u32 indexed_object_tag;
    recovered_u32 second_call_admitted;
    recovered_u32 packet[5];
    recovered_u32 packet_count;
    recovered_u32 first_dispatch_target;
    recovered_u32 second_dispatch_target;
    recovered_u32 first_transform_0;
    recovered_u32 first_transform_1;
    recovered_u32 first_transform_2;
    recovered_u32 second_transform_0;
    recovered_u32 second_transform_1;
    recovered_u32 second_transform_2;
    recovered_u32 completion_word;
    recovered_u32 return_target;
} recovered_geometry_status_scene_arm1_result_e89d4;

recovered_geometry_status_scene_arm1_result_e89d4
recovered_geometry_status_scene_arm1_e89d4(recovered_u32 feature_flags,
                                            recovered_u32 scene_count,
                                            recovered_u32 fixed_object_tag,
                                            recovered_u32 indexed_object_tag)
{
    recovered_geometry_status_scene_arm1_result_e89d4 result;

    result.feature_flags = feature_flags;
    result.scene_count = scene_count;
    result.fixed_object_tag = fixed_object_tag & 0xffU;
    result.indexed_object_tag = indexed_object_tag & 0xffU;
    result.second_call_admitted = (feature_flags & (1U << 3)) != 0U;
    result.packet[0] = 5U;
    result.packet[1] = 19U;
    result.packet[2] = 0x41400000U;
    result.packet[3] = 0x41400000U;
    result.packet[4] = RECOVERED_FLOAT_ONE;
    result.packet_count = 5U;
    result.first_dispatch_target = 0x000e7390U;
    result.second_dispatch_target = 0x000e7390U;
    result.first_transform_0 = 0x49c980U;
    result.first_transform_1 = 0xc0c00000U;
    result.first_transform_2 = 0xc0900000U;
    result.second_transform_0 = 0x49c980U;
    result.second_transform_1 = 0U;
    result.second_transform_2 = 0xc0900000U;
    result.completion_word = 6U;
    result.return_target = 0x000e8adcu;
    return result;
}
