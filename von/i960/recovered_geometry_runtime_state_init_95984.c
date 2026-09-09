/* Fixed state writes following the first geometry-runtime initializer loop. */
#include "recovered_common.h"

struct recovered_geometry_runtime_state_init_95984_plan {
    recovered_u32 constant_address, constant_value;
    recovered_u32 zero_doubleword_address[2];
    recovered_u32 status_table_address, status_word, status_word_count;
    recovered_u32 ready_word_address, ready_word_value;
    recovered_u32 state_cluster_address, state_cluster_word[7];
};

void recovered_geometry_runtime_state_init_95984(
    recovered_u32 seed_word, recovered_u32 status_words[6],
    recovered_u32 state_cluster_words[7],
    struct recovered_geometry_runtime_state_init_95984_plan *plan)
{
    for (unsigned i = 0; i < 6; ++i)
        status_words[i] = seed_word;
    state_cluster_words[0] = seed_word; /* 0x562b40 */
    state_cluster_words[1] = 0U;        /* 0x562b44 */
    state_cluster_words[2] = 0U;        /* 0x562b48 */
    state_cluster_words[3] = 0U;        /* 0x562b4c */
    state_cluster_words[4] = seed_word; /* 0x562b54 */
    state_cluster_words[5] = seed_word; /* 0x562b56 */
    state_cluster_words[6] = seed_word; /* 0x562b58 */

    plan->constant_address = 0x562538U;
    plan->constant_value = 0xc059999aU;
    plan->zero_doubleword_address[0] = 0x5624f0U;
    plan->zero_doubleword_address[1] = 0x562530U;
    plan->status_table_address = 0x5624d0U;
    plan->status_word = seed_word;
    plan->status_word_count = 6U;
    plan->ready_word_address = 0x503aacU;
    plan->ready_word_value = seed_word;
    plan->state_cluster_address = 0x562b40U;
    for (unsigned i = 0; i < 7; ++i)
        plan->state_cluster_word[i] = state_cluster_words[i];
}
