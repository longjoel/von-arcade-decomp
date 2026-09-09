/* Final status-scene arm dispatch recovered from i960 0xe8908-0xe8934. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 input_mode;
    recovered_u32 accepted;
    recovered_u32 mode_address;
    recovered_u32 table_address;
    recovered_u32 target;
    recovered_u32 arm[6];
    recovered_u32 return_target;
} recovered_geometry_status_scene_arm_dispatch_result_e8920;

recovered_geometry_status_scene_arm_dispatch_result_e8920
recovered_geometry_status_scene_arm_dispatch_e8920(recovered_u32 mode)
{
    recovered_geometry_status_scene_arm_dispatch_result_e8920 result;

    result.input_mode = mode;
    result.mode_address = 0x005783c4U;
    result.table_address = 0x000e8920U;
    result.arm[0] = 0x000e8938U;
    result.arm[1] = 0x000e89d4U;
    result.arm[2] = 0x000e8ae0U;
    result.arm[3] = 0x000e8c5cU;
    result.arm[4] = 0x000e8e44U;
    result.arm[5] = 0x000e8fe4U;
    result.return_target = 0x000e9138U;
    result.accepted = mode < 6U;
    result.target = result.accepted ? result.arm[mode] : result.return_target;
    return result;
}
