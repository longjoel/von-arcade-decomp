/* Shared selector tails recovered from i960 0x7d4b4, 0x7d5f4, 0x7d644, 0x7d654. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_selector_shared_tail_7d4b4 {
    u32 writes_selector;
    u32 selector_value;
    u32 writes_continuation;
    u32 continuation_value;
};

void recovered_state_selector_shared_tail_7d4b4(
    u32 target, u32 caller_continuation,
    struct recovered_state_selector_shared_tail_7d4b4 *plan)
{
    plan->writes_selector = 0U;
    plan->selector_value = 0U;
    plan->writes_continuation = 0U;
    plan->continuation_value = 0U;

    switch (target) {
    case 0x0007d4b4U:
        plan->writes_selector = 1U;
        plan->selector_value = 3U;
        break;
    case 0x0007d5f4U:
        plan->writes_selector = 1U;
        plan->selector_value = 2U;
        break;
    case 0x0007d644U:
        plan->writes_selector = 1U;
        plan->selector_value = 1U;
        break;
    case 0x0007d654U:
        plan->writes_continuation = 1U;
        plan->continuation_value = caller_continuation;
        break;
    default:
        break;
    }
}
