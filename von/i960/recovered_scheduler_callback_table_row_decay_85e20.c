/* Callback table row-decay leaf recovered from i960 0x85e20-0x85e90. */

#include <stdint.h>

typedef uint32_t u32;
typedef int32_t s32;

struct recovered_scheduler_callback_table_row_decay_85e20 {
    u32 state;
    u32 selector;
    u32 row_offset;
    s32 current_before;
    s32 current_after;
    s32 paired_before;
    s32 paired_after;
    u32 exits_without_pair_write;
};

struct recovered_scheduler_callback_table_row_decay_85e20
recovered_scheduler_callback_table_row_decay_85e20(
    u32 state, u32 selector, s32 current_value, s32 paired_value)
{
    struct recovered_scheduler_callback_table_row_decay_85e20 out;

    out.state = state;
    out.selector = selector;
    out.row_offset = state * 1152U + selector * 144U + 0x8eU;
    out.current_before = current_value;
    out.current_after = current_value - 10;
    out.paired_before = paired_value;
    out.paired_after = paired_value;
    out.exits_without_pair_write = 0U;

    /* cmpobg paired_value,49 rejects values strictly above 49. */
    if (paired_value > 49) {
        out.exits_without_pair_write = 1U;
    } else {
        out.paired_after = 40;
    }
    return out;
}
