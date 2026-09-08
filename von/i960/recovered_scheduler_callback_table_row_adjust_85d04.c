/* Callback table row adjustment recovered from i960 0x85d04-0x85d54. */

#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_scheduler_callback_table_row_adjust_85d04 {
    u32 state;
    u32 selector;
    u32 row_offset;
    s32 current_before;
    s32 current_after;
    s32 paired_before;
    s32 paired_after;
    u32 paired_capped;
    u32 exits_without_pair_write;
};

struct recovered_scheduler_callback_table_row_adjust_85d04
recovered_scheduler_callback_table_row_adjust_85d04(
    u32 state, u32 selector, s32 current_value, s32 paired_value)
{
    struct recovered_scheduler_callback_table_row_adjust_85d04 out;

    out.state = state;
    out.selector = selector;
    out.row_offset = state * 1152U + selector * 144U + 0x8eU;
    out.current_before = current_value;
    out.current_after = current_value + 30;
    out.paired_before = paired_value;
    out.paired_after = paired_value;
    out.paired_capped = 0U;
    out.exits_without_pair_write = 0U;

    /* cmpoble paired_value,1000 branches directly when paired <= 1000. */
    if (paired_value <= 1000) {
        out.exits_without_pair_write = 1U;
    } else {
        out.paired_after = 1000;
        out.paired_capped = 1U;
    }
    return out;
}
