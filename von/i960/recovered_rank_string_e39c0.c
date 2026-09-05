/* Rank-string emitter recovered from i960 0xe39c0-0xe39e4. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_rank_string_plan {
    u32 number_table;
    u32 suffix_table;
    u32 entry_stride;
    u32 number_walker;
    u32 suffix_walker;
    u32 number_address;
    u32 suffix_address;
};

void recovered_rank_string_plan(u32 index,
                                struct recovered_rank_string_plan *plan)
{
    /* Parallel ordinal tables: 0xe36c0 holds " 1", " 2", ... while
     * 0xe3700 holds "ST", "ND", "RD", "TH", ... The number half goes
     * through the 0x1d1d0 walker and the suffix through 0x1d1b0. */
    plan->number_table = 0x000e36c0U;
    plan->suffix_table = 0x000e3700U;
    /* shlo 1 / addo / shlo 1 scales the index by ((i*2+i)*2) = i*6. */
    plan->entry_stride = 6U;
    plan->number_walker = 0x0001d1d0U;
    plan->suffix_walker = 0x0001d1b0U;
    plan->number_address = plan->number_table + index * plan->entry_stride;
    plan->suffix_address = plan->suffix_table + index * plan->entry_stride;
}
