/* Deterministic record initialization recovered from i960 0x6fb90-0x6fd4c. */
typedef unsigned int u32;
typedef unsigned char u8;

static void store_u16_le(u8 *record, u32 offset, u32 value)
{
    record[offset] = (u8)value;
    record[offset + 1U] = (u8)(value >> 8);
}

static void store_u32_le(u8 *record, u32 offset, u32 value)
{
    record[offset] = (u8)value;
    record[offset + 1U] = (u8)(value >> 8);
    record[offset + 2U] = (u8)(value >> 16);
    record[offset + 3U] = (u8)(value >> 24);
}

/*
 * template_words are the eleven 32-bit values at source offsets 0x04..0x2c.
 * record_bytes is the exact 84-byte destination at 0x51bb30 + slot * 0x54.
 * The source +0x24 word is intentionally narrowed to the unaligned halfword
 * store at destination +0x3e, matching the i960 `stos` instruction.
 */
void recovered_geometry_record_init(const u32 template_words[11],
                                    u32 association_value,
                                    u32 association_is_empty,
                                    u8 record_bytes[84])
{
    u32 index;

    for (index = 0U; index < 84U; ++index)
        record_bytes[index] = 0U;

    store_u32_le(record_bytes, 0x04U, template_words[0]);
    store_u32_le(record_bytes, 0x08U, template_words[1]);
    store_u32_le(record_bytes, 0x0cU, template_words[2]);
    store_u32_le(record_bytes, 0x10U, template_words[3]);
    store_u32_le(record_bytes, 0x14U,
                 association_is_empty ? 999U : association_value);
    store_u32_le(record_bytes, 0x18U, 999U);
    store_u32_le(record_bytes, 0x30U, template_words[4]);
    store_u32_le(record_bytes, 0x34U, template_words[5]);
    store_u32_le(record_bytes, 0x38U, template_words[6]);
    store_u32_le(record_bytes, 0x3cU, template_words[7]);
    store_u16_le(record_bytes, 0x3eU, template_words[8]);
    store_u32_le(record_bytes, 0x40U, template_words[9]);
    store_u32_le(record_bytes, 0x44U, template_words[10]);
}
