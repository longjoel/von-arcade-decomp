/* Caller handoff recovered from i960 0x76934-0x769fc. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 first_result_0;
    recovered_u32 first_result_1;
    recovered_u32 second_result_0;
    recovered_u32 second_result_1;
    recovered_u32 object_flag_1dd;
    recovered_u32 object_flag_1de;
    recovered_u32 object_flag_1df;
} recovered_geometry_profile_pair_publication_input_76934;

typedef struct {
    recovered_u32 first_pair_504e20_504e28[2];
    recovered_u32 second_pair_504e24_504e2c[2];
    recovered_u32 control_504e30;
    recovered_u32 helper_target;
    recovered_u32 shared_output_offset;
    recovered_u32 shared_aux_offset;
} recovered_geometry_profile_pair_publication_result_76934;

/*
 * Both calls pass the same frame-relative output addresses (fp+0x40 and
 * fp+0x44) to 0x778b0.  The caller publishes the first returned pair before
 * making the second call, then synthesizes 0x504e30 from object flag bits:
 * 1dd bit 0 -> value 3, 1df bit 0 -> bit 2, 1de bit 1 -> bit 3, 1dd bit 1
 * -> bit 4, and 1df bit 1 -> bit 5.
 */
void recovered_geometry_profile_pair_publication_76934(
    const recovered_geometry_profile_pair_publication_input_76934 *input,
    recovered_geometry_profile_pair_publication_result_76934 *result)
{
    result->first_pair_504e20_504e28[0] = input->first_result_0;
    result->first_pair_504e20_504e28[1] = input->first_result_1;
    result->second_pair_504e24_504e2c[0] = input->second_result_0;
    result->second_pair_504e24_504e2c[1] = input->second_result_1;
    result->control_504e30 = 1U;
    if ((input->object_flag_1dd & 1U) != 0U)
        result->control_504e30 = 3U;
    if ((input->object_flag_1df & 1U) != 0U)
        result->control_504e30 |= 1U << 2;
    if ((input->object_flag_1de & 2U) != 0U)
        result->control_504e30 |= 1U << 3;
    if ((input->object_flag_1dd & 2U) != 0U)
        result->control_504e30 |= 1U << 4;
    if ((input->object_flag_1df & 2U) != 0U)
        result->control_504e30 |= 1U << 5;
    result->helper_target = 0x000778b0U;
    result->shared_output_offset = 0x40U;
    result->shared_aux_offset = 0x44U;
}
