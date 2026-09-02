/* Contract for the indirect-return thunk at i960 0x1f9c0. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_clear_g14_return_plan {
    u32 return_stub;
    u32 clears_g14;
    u32 branch_register;
};

void recovered_clear_g14_return_plan(struct recovered_clear_g14_return_plan *plan)
{
    plan->return_stub = 0x0001f9d4U;
    plan->clears_g14 = 1U;
    plan->branch_register = 0U;
}
