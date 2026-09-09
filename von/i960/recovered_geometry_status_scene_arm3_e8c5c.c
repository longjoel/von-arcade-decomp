/* Status-scene arm 3 recovered from i960 0xe8c5c-0xe8e40. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 feature_flags;
    recovered_u32 scene_count;
    recovered_u32 object_tag[4];
    recovered_u32 fourth_call_admitted;
    recovered_u32 packet[5];
    recovered_u32 packet_count;
    recovered_u32 dispatch_target;
    recovered_u32 transform_0;
    recovered_u32 transform_1[4];
    recovered_u32 transform_2;
    recovered_u32 completion_word;
    recovered_u32 cleanup_counter_before;
    recovered_u32 cleanup_counter_after;
    recovered_u32 cleanup_triggered;
    recovered_u32 cleanup_count_address;
    recovered_u32 frame_count_address;
    recovered_u32 cleanup_helper_a;
    recovered_u32 cleanup_helper_b;
    recovered_u32 return_target;
} recovered_geometry_status_scene_arm3_result_e8c5c;

recovered_geometry_status_scene_arm3_result_e8c5c
recovered_geometry_status_scene_arm3_e8c5c(recovered_u32 feature_flags,
                                            recovered_u32 scene_count,
                                            recovered_u32 object_tag_0,
                                            recovered_u32 object_tag_1,
                                            recovered_u32 object_tag_2,
                                            recovered_u32 indexed_object_tag,
                                            recovered_u32 cleanup_counter)
{
    recovered_geometry_status_scene_arm3_result_e8c5c result;

    result.feature_flags = feature_flags;
    result.scene_count = scene_count;
    result.object_tag[0] = object_tag_0 & 0xffU;
    result.object_tag[1] = object_tag_1 & 0xffU;
    result.object_tag[2] = object_tag_2 & 0xffU;
    result.object_tag[3] = indexed_object_tag & 0xffU;
    result.fourth_call_admitted = (feature_flags & (1U << 3)) != 0U;
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
    result.transform_1[3] = 0x41400000U;
    result.transform_2 = 0xc0900000U;
    result.completion_word = 6U;
    result.cleanup_counter_before = cleanup_counter;
    result.cleanup_counter_after = cleanup_counter - 1U;
    result.cleanup_triggered = result.cleanup_counter_after == 0U;
    result.cleanup_count_address = 0x00503a04U;
    result.frame_count_address = 0x00503a00U;
    result.cleanup_helper_a = 0x000e54a0U;
    result.cleanup_helper_b = 0x000e37b0U;
    result.return_target = 0x000e8e40U;
    return result;
}
