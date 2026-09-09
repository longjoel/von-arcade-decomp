/* Selection prefix recovered from i960 0x778b0-0x779ec. */
#include <stdint.h>

typedef uint32_t recovered_u32;

struct recovered_match_profile_result_candidate_778b0 {
    int16_t table_word0;
    int16_t table_word2;
    int16_t table_word4;
    uint16_t wrapped_gate_value;
    int32_t returned_metric;
};

struct recovered_match_profile_result_selection_778b0 {
    recovered_u32 selected_index; /* 0..7, or 0xffffffff when absent. */
    int32_t selected_metric;
    recovered_u32 scanned_count;
    recovered_u32 table_base;
    recovered_u32 table_stride;
    recovered_u32 gate_limit;
};

/*
 * The table increments by six bytes and the loop uses the literal-first
 * cmpi 7,r4 / bge form, so indices 0 through 7 are visited.  The FIFO
 * request/response work is represented by the already observed gate and
 * returned metric for each candidate; packet construction begins at 0x779f0.
 */
struct recovered_match_profile_result_selection_778b0
recovered_match_profile_result_select_778b0(
    const struct recovered_match_profile_result_candidate_778b0 candidates[8])
{
    struct recovered_match_profile_result_selection_778b0 out = {
        0xffffffffU, 0, 8U, 0x00505060U, 6U, 0x7ffeU
    };
    int i;

    for (i = 0; i < 8; ++i) {
        if (candidates[i].table_word4 == 0)
            continue;
        if (candidates[i].wrapped_gate_value > 0x7ffeU)
            continue;
        if (out.selected_index == 0xffffffffU ||
            candidates[i].returned_metric < out.selected_metric) {
            out.selected_index = (recovered_u32)i;
            out.selected_metric = candidates[i].returned_metric;
        }
    }
    return out;
}
