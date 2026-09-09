/* First admission loop of the paired-object scanner at i960 0xbd8e0. */
#include "recovered_common.h"

typedef struct {
    uint8_t active[32];
    uint16_t preceding_halfword[32];
    uint16_t current_halfword[32];
    recovered_u32 linked_word_0c[32];
    recovered_u32 linked_word_10[32];
    recovered_u32 linked_word_14[32];
    recovered_u32 mode_table_word_24[256];
    recovered_u32 mode_table_word_28[256];
} recovered_object_dual_admission_input_bd8e0;

typedef struct {
    recovered_u32 admitted_index[32];
    recovered_u32 packet_prefix[32][6];
    recovered_u32 admitted_count;
} recovered_object_dual_admission_result_bd8e0;

/* The later paired-object packet and response logic begins after this gate.
 * This contract preserves only the directly proven three-part predicate. */
void recovered_object_dual_admission_bd8e0(
    const recovered_object_dual_admission_input_bd8e0 *input,
    recovered_object_dual_admission_result_bd8e0 *result)
{
    recovered_u32 index;
    result->admitted_count = 0U;
    for (index = 0U; index < 32U; ++index) {
        if (input->active[index] == 0U)
            continue;
        if ((input->preceding_halfword[index] & 0x8000U) == 0U)
            continue;
        if ((input->current_halfword[index] & 0x8000U) != 0U)
            continue;
        recovered_u32 admitted = result->admitted_count++;
        recovered_u32 table_index = input->active[index];
        result->admitted_index[admitted] = index;
        result->packet_prefix[admitted][0] = 72U;
        result->packet_prefix[admitted][1] = input->linked_word_0c[index];
        result->packet_prefix[admitted][2] = input->linked_word_10[index];
        result->packet_prefix[admitted][3] = input->linked_word_14[index];
        result->packet_prefix[admitted][4] = input->mode_table_word_24[table_index];
        result->packet_prefix[admitted][5] = input->mode_table_word_28[table_index];
    }
}
