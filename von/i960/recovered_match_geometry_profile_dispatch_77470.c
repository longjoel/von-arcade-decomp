/* Profile dispatch prefix recovered from i960 0x77470-0x77508. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 global_504d94;
    recovered_u32 global_504db4;
    recovered_u32 normalized_geometry_bits;
} recovered_match_geometry_profile_dispatch_input_77470;

typedef struct {
    recovered_u32 profile_index;
    recovered_u32 valid_profile_index;
    recovered_u32 dispatch_target;
    recovered_u32 special_geometry_override;
    recovered_u32 geometry_bits;
} recovered_match_geometry_profile_dispatch_result_77470;

void recovered_match_geometry_profile_dispatch_77470(
    const recovered_match_geometry_profile_dispatch_input_77470 *input,
    recovered_match_geometry_profile_dispatch_result_77470 *result)
{
    static const recovered_u32 targets[21] = {
        0x000775e0U, 0x0007755cU, 0x00077574U, 0x00077590U,
        0x000775acU, 0x000775c4U, 0x00077834U, 0x000775e0U,
        0x00077650U, 0x0007766cU, 0x00077684U, 0x00077834U,
        0x00077834U, 0x000776a0U, 0x000776b8U, 0x000776d4U,
        0x000776f0U, 0x00077764U, 0x0007777cU, 0x00077798U,
        0x000777b0U
    };
    recovered_u32 index = input->global_504d94 - 1U;

    result->profile_index = index;
    result->special_geometry_override =
        (index <= 5U && input->global_504db4 == 0U) ? 1U : 0U;
    result->geometry_bits = result->special_geometry_override
        ? 0x42c80000U : input->normalized_geometry_bits;
    result->valid_profile_index = index <= 20U ? 1U : 0U;
    result->dispatch_target = result->valid_profile_index
        ? targets[index] : 0x00077834U;
}
