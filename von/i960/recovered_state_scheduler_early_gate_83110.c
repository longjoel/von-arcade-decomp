/* Early gate recovered from i960 0x83110-0x83148. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_scheduler_early_gate_83110 {
    u32 terminal;
    u32 write_504d98;
    u32 value_504d98;
};

struct recovered_state_scheduler_early_gate_83110
recovered_state_scheduler_early_gate_83110(int32_t value_504dc0,
                                           int32_t related_state, u32 caller_g14)
{
    struct recovered_state_scheduler_early_gate_83110 out = {0U, 0U, 0U};

    if (value_504dc0 <= 149
        && (related_state == 19 || related_state == 20)) {
        out.terminal = 1U;
        out.write_504d98 = 1U;
        out.value_504d98 = caller_g14;
    }
    return out;
}
