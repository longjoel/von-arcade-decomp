/* Shared deterministic core of i960 profile loaders 0x6f900 and 0x6f970. */
typedef unsigned int u32;

struct recovered_geometry_profile_table_record {
    u32 word0;
    u32 word1;
    u32 word2;
    u32 word3;
    u32 word4;
    u32 word5;
};

struct recovered_geometry_profile_table_output {
    u32 published_pair_low;
    u32 published_pair_high;
    u32 published_word;
    u32 fifo_selector;
    u32 fifo_record_word;
};

/*
 * The ROM scales g0 by 24 bytes (g0*3 then <<3), reads record words 0/1,
 * 3, and 5, sets bit 6 in the incoming g1 selector, and returns through g2.
 * Both loader entries share this body; only their local return stub differs.
 */
void recovered_geometry_profile_table_loader(
    u32 profile_index,
    u32 incoming_selector,
    const struct recovered_geometry_profile_table_record *table,
    struct recovered_geometry_profile_table_output *output)
{
    const struct recovered_geometry_profile_table_record *record =
        &table[profile_index];

    output->published_pair_low = record->word0;
    output->published_pair_high = record->word1;
    output->published_word = record->word3;
    output->fifo_selector = incoming_selector | 0x40U;
    output->fifo_record_word = record->word5;
}
