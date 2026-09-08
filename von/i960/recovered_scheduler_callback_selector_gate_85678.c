/* Callback selector gate recovered from i960 0x85678-0x8568c. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_scheduler_callback_selector_gate_85678 {
    u32 selector;
    u32 enters_selector1_path;
    u32 branches_to_85784;
};

struct recovered_scheduler_callback_selector_gate_85678
recovered_scheduler_callback_selector_gate_85678(u32 selector)
{
    struct recovered_scheduler_callback_selector_gate_85678 out = {
        selector, 0U, 0U
    };

    /* cmpibne 1,g7: all selectors other than 1 skip to 0x85784. */
    out.enters_selector1_path = selector == 1U ? 1U : 0U;
    out.branches_to_85784 = selector == 1U ? 0U : 1U;
    return out;
}
