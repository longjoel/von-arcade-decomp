/* Object dispatch gate recovered from i960 0x81e60-0x81eb2. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_dispatch_gate_plan {
    u32 mode_match;
    u32 sub_mode_match;
    u32 pre_call;
    u32 calls_pre;
    u32 state_max;
    u32 table_base;
    u32 table_targets[10];
    u32 target;
};

static const u32 recovered_dispatch_targets[10] = {
    0x00081edcU, 0x00081ee8U, 0x00081ef4U, 0x00081f00U, 0x00081f0cU,
    0x00081f18U, 0x00081f24U, 0x00081f30U, 0x00081f3cU, 0x00081f48U
};

void recovered_dispatch_gate_plan(u32 mode, u32 sub_mode, u32 flag,
                                  u32 state,
                                  struct recovered_dispatch_gate_plan *plan)
{
    u32 index;

    plan->mode_match = 4U;
    plan->sub_mode_match = 10U;
    plan->pre_call = 0x00084d90U;
    /* Only the 0x84d90 pre-call is mode-gated; the table dispatch below
     * depends solely on the flag and the state bound. */
    plan->calls_pre = (mode == plan->mode_match
        && sub_mode == plan->sub_mode_match && flag != 0U) ? 1U : 0U;
    plan->state_max = 9U;
    plan->table_base = 0x00081eb4U;
    for (index = 0U; index < 10U; ++index)
        plan->table_targets[index] = recovered_dispatch_targets[index];
    /* cmpobl compares literal-first, so states above 9 exit while 0-9
     * index the table; r4 still holds the entry object for the target. */
    plan->target = (flag != 0U && state <= plan->state_max)
        ? recovered_dispatch_targets[state] : 0U;
}
