/* Response-helper completion gate recovered from i960 0x8d090-0x8d0a4. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 status_word;
    recovered_u32 status_offset;
    recovered_u32 completion_address, completion_value;
    recovered_u32 returned;
    recovered_u32 retry_target;
} recovered_startup_mode4_arm_result_8d090_completion_gate;

int recovered_startup_mode4_arm_8d090_completion_gate(
    recovered_u32 status_word,
    recovered_startup_mode4_arm_result_8d090_completion_gate *result)
{
    recovered_startup_mode4_arm_result_8d090_completion_gate r = {0};
    r.status_word = status_word;
    r.status_offset = 0x30U;
    r.completion_address = 0x51c9b4U;
    r.completion_value = status_word == 0U ? 1U : 0U;
    r.returned = status_word == 0U ? 1U : 0U;
    r.retry_target = 0x8ccf0U;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
