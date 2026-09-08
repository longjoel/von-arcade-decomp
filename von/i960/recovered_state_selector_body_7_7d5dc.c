/* State-7 selector body recovered from i960 0x7d5dc-0x7d604. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_selector_body_7_7d5dc_plan {
    u32 target;
    u32 writes_selector;
    u32 selector_value;
};

void recovered_state_selector_body_7_7d5dc(
    u32 mode_bits, u32 control_504dc8,
    struct recovered_state_selector_body_7_7d5dc_plan *plan)
{
    plan->target = 0x0007d654U;
    plan->writes_selector = 0U;
    plan->selector_value = 0U;

    if ((mode_bits & (1U << 1)) == 0U || control_504dc8 != 1U)
        return;

    plan->target = 0x0007d5f4U;
    plan->writes_selector = 1U;
    plan->selector_value = 2U;
}
