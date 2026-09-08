/* State-31 global/callback gate recovered from 0x7ecc0-0x7ed20. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state31_global_callback_gate_7ecc0_plan {
    u32 global_5770f0;
    u32 global_gate_passed;
    u32 best_response_zero;
    u32 callback_target;
    u32 callback_selector;
    u32 first_continuation;
    u32 second_zero_test_passed;
    u32 selector_gate_passed;
    u32 status_gate_passed;
    u32 continues_to_7ed34;
    u32 failure_target;
};

void recovered_state31_global_callback_gate_7ecc0(
    u32 global_5770f0, u32 best_response_zero, u32 selected_mask,
    u32 selector_504e4c, u32 status_504d68,
    struct recovered_state31_global_callback_gate_7ecc0_plan *plan)
{
    const u32 global_passed = global_5770f0 > 9U;
    const u32 response_zero = best_response_zero != 0U ? 1U : 0U;
    const u32 selector_passed = selector_504e4c == 0U ||
                                selector_504e4c == 2U ||
                                selector_504e4c == 5U;
    const u32 status_passed = status_504d68 == 0U || status_504d68 == 9U;
    const u32 continues = response_zero && selector_passed && status_passed;

    plan->global_5770f0 = global_5770f0;
    plan->global_gate_passed = global_passed;
    plan->best_response_zero = response_zero;
    plan->callback_target = response_zero ? 0x00081b30U : 0x000816d0U;
    plan->callback_selector = response_zero ? 0U : selected_mask;
    plan->first_continuation = 0x0007ed08U;
    plan->second_zero_test_passed = response_zero;
    plan->selector_gate_passed = response_zero && selector_passed;
    plan->status_gate_passed = response_zero && status_passed;
    plan->continues_to_7ed34 = continues;
    plan->failure_target = plan->continues_to_7ed34 ? 0U :
                           (response_zero && selector_passed ? 0x0007ee28U :
                                                               0x0007f0f8U);
}
