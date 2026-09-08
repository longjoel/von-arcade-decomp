/* Early gate recovered from i960 0x83cc0-0x83cf8. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_scheduler_early_gate_83cc0 {
    u32 terminal;
    u32 write_504d98;
    u32 value_504d98;
    u32 continues;
};

struct recovered_state_scheduler_early_gate_83cc0
recovered_state_scheduler_early_gate_83cc0(int32_t value_504dc0,
                                           int32_t related_state, u32 caller_g14)
{
    struct recovered_state_scheduler_early_gate_83cc0 out = {
        0U, 0U, 0U, 1U
    };

    if (value_504dc0 <= 149
        && (related_state == 19 || related_state == 20)) {
        out.terminal = 1U;
        out.write_504d98 = 1U;
        out.value_504d98 = caller_g14;
        out.continues = 0U;
    }
    return out;
}
