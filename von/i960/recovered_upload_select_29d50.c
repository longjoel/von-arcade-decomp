/* Upload bank-select prologue recovered from i960 0x29d50-0x29dbc. */
#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_upload_select_plan {
    u32 counter_addr;
    u32 mode_addr;
    s32 active;
    s32 old_counter;
    s32 next_counter;
    u32 src0_addr;
    u32 dst0_addr;
    u32 src1_addr;
    u32 dst1_addr;
    u32 src2_addr;
    u32 dst2_addr;
    u32 mode;
    s32 direct_path;
};

void recovered_upload_select_plan(s32 counter, u32 mode,
                                   struct recovered_upload_select_plan *plan)
{
    plan->counter_addr = 0x0051a264U;
    plan->mode_addr = 0x0051a268U;
    plan->old_counter = counter;
    plan->mode = mode;
    /* cmpibge 3,r7,0x29d6c: counters below 3 restore g4 and return. */
    plan->active = counter >= 3 ? 1 : 0;
    if (!plan->active) {
        plan->next_counter = counter;
        plan->src0_addr = 0U;
        plan->dst0_addr = 0U;
        plan->src1_addr = 0U;
        plan->dst1_addr = 0U;
        plan->src2_addr = 0U;
        plan->dst2_addr = 0U;
        plan->direct_path = 0;
        return;
    }
    /* shlo 12,r7,r5 selects a 4KB bank, then addo r7,1 stores the bump. */
    plan->next_counter = counter + 1;
    {
        u32 bank = (u32)counter << 12;
        plan->src0_addr = 0x01810100U + bank;
        plan->dst0_addr = 0x01810000U + bank;
        plan->src1_addr = 0x01814100U + bank;
        plan->dst1_addr = 0x01814000U + bank;
        plan->src2_addr = 0x01818100U + bank;
        plan->dst2_addr = 0x01818000U + bank;
    }
    /* cmpi r6,0 / be 0x29f60: a zero mode word takes the direct path. */
    plan->direct_path = mode == 0U ? 1 : 0;
}
