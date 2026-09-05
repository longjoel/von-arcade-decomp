/* Counter dispatch schedule recovered from i960 0x1b9d0-0x1ba08.
 *
 * The routine masks the service counter at 0x503a04 down to bit 5 for
 * a caller-owned 0x1fa30 sub-call, then dispatches on bit 4 of the
 * flag byte at 0x5024a4: a set bit jumps straight to the link-publish
 * block at 0x1ba08 (see recovered_link_publish_1ba08.c) with no store,
 * otherwise the counter is decremented in place (cmpdeci) and only a
 * counter that just reached... precisely, only an entry counter of 1
 * (stored back as 0) falls through to the link block; anything else
 * returns. Sub-call bodies stay caller-owned.
 */
#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;
typedef uint8_t u8;

struct recovered_counter_dispatch_plan {
    u32 counter_addr;
    u32 call_arg;
    s32 do_store;
    u32 stored_counter;
    s32 take_link_block;
};

void recovered_counter_dispatch_plan(u32 counter, u8 flag,
                                      struct recovered_counter_dispatch_plan *plan)
{
    plan->counter_addr = 0x00503a04U;
    /* addo 31,1 then and: the 0x1fa30 call receives counter & 32. */
    plan->call_arg = counter & 32U;
    /* bbs 4: a set flag bit bypasses the decrement store entirely. */
    if ((flag >> 4) & 1U) {
        plan->do_store = 0;
        plan->stored_counter = counter;
        plan->take_link_block = 1;
        return;
    }
    /* cmpdeci 1: store counter - 1, then bne exits unless the entry
     * counter was exactly 1. */
    plan->do_store = 1;
    plan->stored_counter = counter - 1U;
    plan->take_link_block = counter == 1U ? 1 : 0;
}
