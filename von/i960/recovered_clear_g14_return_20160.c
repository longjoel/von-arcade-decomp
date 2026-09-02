/* Clear-g14 indirect return thunk recovered from i960 0x20160. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_clear_g14_return_20160_plan {
    u32 return_stub;
    u32 clears_g14;
    u32 branch_register;
};

void recovered_clear_g14_return_20160_plan(
    struct recovered_clear_g14_return_20160_plan *plan)
{
    plan->return_stub = 0x00020174U;
    plan->clears_g14 = 1U;
    plan->branch_register = 0U;
}
