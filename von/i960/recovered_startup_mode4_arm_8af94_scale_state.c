/* Selector-2 scale/state boundary recovered from i960 0x8af94-0x8b0b0. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 selected_float;
    recovered_u32 scale_result;
    recovered_u32 positive_packet_word;
    recovered_u32 nonpositive_packet_word;
    recovered_u32 state_51c948;
    recovered_u32 state_51c94c;
    recovered_u32 positive_path;
    recovered_u32 state_continuation;
    recovered_u32 positive_continuation;
} recovered_startup_mode4_arm_8af94_scale_state_result;

recovered_startup_mode4_arm_8af94_scale_state_result
recovered_startup_mode4_arm_8af94_scale_state(
    recovered_u32 selected_float, recovered_u32 scale_result,
    recovered_u32 positive_packet_word, recovered_u32 nonpositive_packet_word,
    recovered_u32 positive_path)
{
    recovered_startup_mode4_arm_8af94_scale_state_result result;

    result.selected_float = selected_float;
    result.scale_result = scale_result;
    result.positive_packet_word = positive_packet_word;
    result.nonpositive_packet_word = nonpositive_packet_word;
    result.state_51c948 = scale_result;
    result.positive_path = positive_path != 0U ? 1U : 0U;
    result.state_51c94c = result.positive_path != 0U ?
        positive_packet_word : nonpositive_packet_word;
    result.state_continuation = 0x0008b0b0U;
    result.positive_continuation = result.positive_path != 0U ?
        0x0008b004U : 0x0008b080U;
    return result;
}
