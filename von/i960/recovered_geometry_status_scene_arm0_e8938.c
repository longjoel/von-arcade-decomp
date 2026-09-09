/* Status-scene arm 0 recovered from i960 0xe8938-0xe89d0. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 feature_flags;
    recovered_u32 scene_count;
    recovered_u32 object_tag;
    recovered_u32 admitted;
    recovered_u32 fifo_word[5];
    recovered_u32 fifo_count;
    recovered_u32 object_dispatch_target;
    recovered_u32 transform_0;
    recovered_u32 transform_1;
    recovered_u32 transform_2;
    recovered_u32 completion_word;
    recovered_u32 return_target;
} recovered_geometry_status_scene_arm0_result_e8938;

recovered_geometry_status_scene_arm0_result_e8938
recovered_geometry_status_scene_arm0_e8938(recovered_u32 feature_flags,
                                            recovered_u32 scene_count,
                                            recovered_u32 object_tag)
{
    recovered_geometry_status_scene_arm0_result_e8938 result;

    result.feature_flags = feature_flags;
    result.scene_count = scene_count;
    result.object_tag = object_tag & 0xffU;
    result.admitted = (feature_flags & (1U << 3)) != 0U;
    result.fifo_word[0] = 5U;
    result.fifo_word[1] = 19U;
    result.fifo_word[2] = 0x41400000U;
    result.fifo_word[3] = 0x41400000U;
    result.fifo_word[4] = RECOVERED_FLOAT_ONE;
    result.fifo_count = 5U;
    result.object_dispatch_target = 0x000e7390U;
    result.transform_0 = 0x49c980U;
    result.transform_1 = 0xc0c00000U;
    result.transform_2 = 0xc0900000U;
    result.completion_word = 6U;
    result.return_target = 0x000e89d0U;
    return result;
}
