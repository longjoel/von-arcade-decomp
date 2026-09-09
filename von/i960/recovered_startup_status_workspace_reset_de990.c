/* Startup status reset prefix recovered from i960 0xde990-0xde9ec. */
#include "recovered_common.h"

typedef struct {
    int32_t stage_503b00;
    int32_t state_504100;
    int32_t mode_504134;
} recovered_startup_status_workspace_reset_input_de990;

typedef struct {
    recovered_u32 cleared_503c9c;
    recovered_u32 cleared_503c98;
    recovered_u32 cleared_50429c;
    recovered_u32 cleared_504298;
    recovered_u32 mode_is_9;
    recovered_u32 continuation;
} recovered_startup_status_workspace_reset_result_de990;

/*
 * The two 0x503c fields are always cleared.  The 0x50429c/0x504298 pair is
 * cleared only by the literal-first stage/state gate, and mode 9 is the only
 * path that falls through to the packet setup at 0xde9ec.
 */
void recovered_startup_status_workspace_reset_de990(
    const recovered_startup_status_workspace_reset_input_de990 *input,
    recovered_startup_status_workspace_reset_result_de990 *result)
{
    result->cleared_503c9c = 1U;
    result->cleared_503c98 = 1U;
    result->cleared_50429c =
        input->stage_503b00 == 4 && input->state_504100 == 1 ? 1U : 0U;
    result->cleared_504298 = result->cleared_50429c;
    result->mode_is_9 = input->mode_504134 == 9 ? 1U : 0U;
    result->continuation = result->mode_is_9 ? 0x000de9ecU : 0x000dead4U;
}
