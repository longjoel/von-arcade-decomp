/* Cluster re-arm stores recovered from i960 0x29c50-0x29c9c.
 *
 * The 0x29c50 entry loads the forced link 0x29c9c, clamps g0 with a
 * zero floor (cmpi g0,0 sends negatives to 0, then the same 0x100
 * ceiling as the 0x29c08 clamp), stores the forced link to the counter
 * slot — 0x29c9c is far above the sub-3 guard, so the next 0x29d50
 * call is active — and the entry g1 to the mode slot, returning
 * one-way through bx(g2) to the ret at 0x29c9c.
 *
 * The 0x29c58 entry skips the forced link: the counter takes the
 * caller's link instead (link-valued at the three known callers
 * 0x1a7c0, 0xdc338, 0xdc77c) with the same zero-floor clamp.
 */
#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_rearm_store_plan {
    u32 value_addr;
    s32 value_stored;
    u32 counter_addr;
    u32 counter_stored;
    u32 mode_addr;
    u32 mode_stored;
    s32 uploader_active;
};

#define RECOVERED_REARM_FORCED_LINK 0x00029c9cU

static s32 recovered_rearm_clamp(s32 value)
{
    if (value < 0)
        return 0;
    if (value > 0x100)
        return 0x100;
    return value;
}

void recovered_rearm_store_plan(s32 value, u32 mode,
                                 struct recovered_rearm_store_plan *plan)
{
    plan->value_addr = 0x0051a260U;
    plan->value_stored = recovered_rearm_clamp(value);
    plan->counter_addr = 0x0051a264U;
    plan->counter_stored = RECOVERED_REARM_FORCED_LINK;
    plan->mode_addr = 0x0051a268U;
    plan->mode_stored = mode;
    plan->uploader_active = 1;
}

void recovered_rearm_link_store_plan(s32 value, u32 link, u32 mode,
                                      struct recovered_rearm_store_plan *plan)
{
    plan->value_addr = 0x0051a260U;
    plan->value_stored = recovered_rearm_clamp(value);
    plan->counter_addr = 0x0051a264U;
    plan->counter_stored = link;
    plan->mode_addr = 0x0051a268U;
    plan->mode_stored = mode;
    /* The 0x29d50 guard compares signed: only links at 3 or above
     * leave the uploader active. */
    plan->uploader_active = (s32)link >= 3 ? 1 : 0;
}
