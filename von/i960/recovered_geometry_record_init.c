/* Deterministic record initialization recovered from i960 0x6fb90-0x6fd4c. */
typedef unsigned int u32;

/*
 * template_words are the eleven 32-bit values at source offsets 0x04..0x2c.
 * record_words models the 84-byte destination at 0x51bb30 + slot * 0x54,
 * using its aligned 32-bit fields at offsets 0, 4, ..., 0x50.
 */
void recovered_geometry_record_init(const u32 template_words[11],
                                    u32 association_value,
                                    u32 association_is_empty,
                                    u32 record_words[21])
{
    u32 index;

    for (index = 0U; index < 21U; ++index)
        record_words[index] = 0U;

    record_words[1] = template_words[0];
    record_words[2] = template_words[1];
    record_words[3] = template_words[2];
    record_words[4] = template_words[3];
    record_words[5] = association_is_empty ? 999U : association_value;
    record_words[6] = 999U;
    record_words[12] = template_words[5];
    record_words[13] = template_words[6];
    record_words[14] = template_words[7];
    record_words[15] = template_words[8];
    record_words[16] = template_words[9];
    record_words[17] = template_words[10];
}
