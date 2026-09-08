/* First deterministic state-update slice recovered from i960 0x3540-0x3580. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_input_state_step_3540 {
    u32 cleared_status_byte;
    u32 bit3_set;
    u32 next_state;
};

void recovered_input_state_step_3540(u32 packed_state, u32 status_byte,
                                     struct recovered_input_state_step_3540 *out)
{
    u32 state = packed_state;

    out->cleared_status_byte = 1U;
    out->bit3_set = (status_byte & 0x08U) != 0U ? 1U : 0U;
    if (out->bit3_set != 0U) {
        /* cmpibl 15,state branches only when state is greater than 15. */
        if (state <= 15U)
            ++state;
    } else {
        state = 0U;
    }
    out->next_state = state;
}
