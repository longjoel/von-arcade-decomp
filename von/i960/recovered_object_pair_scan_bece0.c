/* Deterministic paired object scan recovered from i960 0xbece0-0xbedd0. */
#include "recovered_common.h"

typedef struct {
    uint8_t object_table[2][32];
    uint16_t record_halfword[2][32];
    recovered_u32 object_word_68[2];
} recovered_object_pair_scan_input_bece0;

typedef struct {
    recovered_u32 accepted_object[64];
    recovered_u32 accepted_index[64];
    recovered_u32 dispatch_target[64];
    recovered_u32 suppressed_bit8[64];
    recovered_u32 rejected_above_cc[64];
    recovered_u32 accepted_count;
    recovered_u32 suppressed_count;
    recovered_u32 rejected_count;
    recovered_u32 final_global_565e20;
} recovered_object_pair_scan_result_bece0;

/*
 * Each half of the routine publishes object+0x68 before scanning its 32
 * entries. Values through 0xcc enter the table path; bit 8 in the record
 * halfword suppresses the indirect call, while values above 0xcc take the
 * diagnostic path. Both non-call paths are reported rather than collapsed.
 */
void recovered_object_pair_scan_bece0(
    const recovered_object_pair_scan_input_bece0 *input,
    const recovered_u32 dispatch_table[256],
    recovered_object_pair_scan_result_bece0 *result)
{
    recovered_u32 object;
    recovered_u32 index;

    result->accepted_count = 0U;
    result->suppressed_count = 0U;
    result->rejected_count = 0U;
    result->final_global_565e20 = 0U;
    for (object = 0U; object < 2U; ++object) {
        result->final_global_565e20 = input->object_word_68[object];
        for (index = 0U; index < 32U; ++index) {
            recovered_u32 value = input->object_table[object][index];
            if (value > 0xccU) {
                recovered_u32 rejected = result->rejected_count++;
                result->rejected_above_cc[rejected] = (object << 8) | index;
                continue;
            }
            if ((input->record_halfword[object][index] & 0x100U) != 0U) {
                recovered_u32 suppressed = result->suppressed_count++;
                result->suppressed_bit8[suppressed] = (object << 8) | index;
                continue;
            }
            recovered_u32 accepted = result->accepted_count++;
            result->accepted_object[accepted] = object;
            result->accepted_index[accepted] = index;
            result->dispatch_target[accepted] = dispatch_table[value];
        }
    }
}
