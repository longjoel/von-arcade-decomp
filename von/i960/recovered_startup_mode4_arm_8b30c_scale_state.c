/* Selector-3 scale/state boundary recovered from i960 0x8b30c-0x8b3f4. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 selected_float;
    recovered_u32 scale_result;
    recovered_u32 positive_packet_word;
    recovered_u32 nonpositive_packet_word;
    recovered_u32 state_51c948;
    recovered_u32 state_51c94c;
    recovered_u32 positive_path;
    recovered_u32 branch_target;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_8b30c_scale_state_result;

recovered_startup_mode4_arm_8b30c_scale_state_result
recovered_startup_mode4_arm_8b30c_scale_state(
    recovered_u32 selected_float, recovered_u32 scale_result,
    recovered_u32 positive_packet_word, recovered_u32 nonpositive_packet_word,
    recovered_u32 positive_path)
{
    recovered_startup_mode4_arm_8b30c_scale_state_result result;

    result.selected_float = selected_float;
    result.scale_result = scale_result;
    result.positive_packet_word = positive_packet_word;
    result.nonpositive_packet_word = nonpositive_packet_word;
    result.state_51c948 = scale_result;
    result.positive_path = positive_path != 0U ? 1U : 0U;
    result.state_51c94c = result.positive_path != 0U ?
        positive_packet_word : nonpositive_packet_word;
    result.branch_target = result.positive_path != 0U ?
        0x0008b004U : 0x0008b080U;
    result.continuation = 0x0008b3f4U;
    return result;
}
