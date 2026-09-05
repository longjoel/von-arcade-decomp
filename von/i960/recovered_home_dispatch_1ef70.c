/* Cursor-home dispatch recovered from i960 0x1ef70-0x1efbc. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_home_dispatch_plan {
    u32 home_addrs[3];
    u32 home_values[3];
    u32 use_fill;
    u32 fill_width;
    u32 fill_rows;
    u32 fill_callee;
    u32 emit_string;
    u32 emit_width;
    u32 emit_rows;
    u32 emit_callee;
};

void recovered_home_dispatch_plan(u32 selector,
                                  struct recovered_home_dispatch_plan *plan)
{
    /* Homes three cursor words before branching: 16 to 0x504cdc and
     * 0x504ce0 (column), 18 to 0x504ce4 (row). */
    plan->home_addrs[0] = 0x00504cdcU;
    plan->home_addrs[1] = 0x00504ce0U;
    plan->home_addrs[2] = 0x00504ce4U;
    plan->home_values[0] = 16U;
    plan->home_values[1] = 16U;
    plan->home_values[2] = 18U;
    /* be on the zero test: a zero selector fills, anything else emits. */
    plan->use_fill = selector == 0U ? 1U : 0U;
    plan->fill_width = 32U;
    plan->fill_rows = 6U;
    plan->fill_callee = 0x0001df00U;
    plan->emit_string = 0x02fd6d20U;
    plan->emit_width = 32U;
    plan->emit_rows = 6U;
    plan->emit_callee = 0x0001dc90U;
}
