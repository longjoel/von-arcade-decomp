/*
 * Recovered plain-text path from i960 helpers 0x0001cac8, 0x0001cc40,
 * and 0x0001ccd0.
 *
 * This deliberately does not implement the general formatter at 0x000f5100.
 * Callers here provide only static strings without format directives.
 */

typedef unsigned int u32;
typedef unsigned short u16;
typedef unsigned char u8;

#define TEXT_STATE_ORIGIN ((volatile u32 *)0x00504cdc)
#define TEXT_STATE_COLUMN ((volatile u32 *)0x00504ce0)
#define TEXT_STATE_ROW    ((volatile u32 *)0x00504ce4)
#define TILE_RAM          ((volatile u16 *)0x01000000)
#define TILE_CONTROL      (*(volatile u32 *)0x01800000)
#define VIDEO_STATE       ((volatile u16 *)0x00504d24)

static const u32 VIDEO_CLEAR_ADDRESSES[4] = {
    0x01000000U, 0x0100c000U, 0x01008000U, 0x0100a000U
};
static const u32 VIDEO_CLEAR_HALWORDS[4] = {0x4000U, 0x1000U, 0x0800U, 8U};
static const u32 GLYPH_TABLES[4] = {
    0x02ea11d0U, 0x02ea14d0U, 0x02ea17d0U, 0x02ea1ad0U
};
static const u32 VOLTAGE_WARNING_COLUMNS[4] = {4U, 4U, 4U, 20U};
static const u32 VOLTAGE_WARNING_ROWS[4] = {16U, 19U, 25U, 28U};
static const u32 VOLTAGE_WARNING_TEXTS[4] = {
    0x000012e0U, 0x000012f0U, 0x00001310U, 0x00001320U
};

enum recovered_startup_transfer_kind {
    RECOVERED_STARTUP_WORD_EXPAND = 0U,
    RECOVERED_STARTUP_HALFWORD_SWAP = 1U,
    RECOVERED_STARTUP_HALFWORD_FILL = 2U
};

struct recovered_startup_transfer {
    u32 kind;
    u32 destination;
    u32 source_or_value;
    u32 units;
};

/* 0x1bce0/0x1bd00: profile zero's paired block-conversion source tables. */
static const u32 STARTUP_PROFILE_ZERO_SOURCES[2][3] = {
    {0x02fdef20U, 0x02fd6ea0U, 0x02ff7568U},
    {0x02fdf540U, 0x02fd7460U, 0x02ff7568U}
};
static const u32 STARTUP_PROFILE_ZERO_BLOCKS[3] = {0x31U, 0x2eU, 0x0dU};

/* 0x1bd60/0x1bd80: nonzero profile's paired conversion tables. */
static const u32 STARTUP_PROFILE_NONZERO_SOURCES[2][2] = {
    {0x02fdef20U, 0x02fed0e8U},
    {0x02fdf540U, 0x02fedaa8U}
};
static const u32 STARTUP_PROFILE_NONZERO_BLOCKS[2] = {0x31U, 0x4eU};

void recovered_text_emit_glyph(u32 character, u32 font_mode, u32 attributes);
void recovered_memory_copy_forward(volatile u8 *destination,
                                   volatile const u8 *source,
                                   u32 bytes);
void recovered_host_fatal_halt(void);

void recovered_text_set_position(u32 column, u32 row)
{
    *TEXT_STATE_ORIGIN = column;
    *TEXT_STATE_COLUMN = column;
    *TEXT_STATE_ROW = row;
}

void recovered_text_emit_char(u8 character)
{
    u32 column = *TEXT_STATE_COLUMN;
    u32 row = *TEXT_STATE_ROW;

    if (character > 31U) {
        TILE_RAM[(row << 6) + column] = (u16)(0x8000U | character);
        if (column <= 61U)
            *TEXT_STATE_COLUMN = column + 1U;
        return;
    }

    if (character == 9U) {
        column = (column + 8U) & ~7U;
        if (column > 61U) {
            *TEXT_STATE_COLUMN = 0;
            if (row <= 46U)
                *TEXT_STATE_ROW = row + 1U;
        } else {
            *TEXT_STATE_COLUMN = column;
        }
    } else if (character == 10U) {
        *TEXT_STATE_COLUMN = *TEXT_STATE_ORIGIN;
        if (row <= 46U)
            *TEXT_STATE_ROW = row + 1U;
    }
}

void recovered_text_write_string(volatile const u8 *text)
{
    u8 character;

    while ((character = *text++) != 0)
        recovered_text_emit_char(character);
}

/*
 * The 0x1da90 string helper selects glyph mode 1 unless a lowercase ASCII
 * byte appears after the first byte.  The per-character calls into 0x1d310
 * remain outside this pure classifier.
 */
u32 recovered_text_string_font_mode(const u8 *text)
{
    const u8 *cursor = text;
    u32 mode = 1U;

    if (*cursor == 0U)
        return mode;
    ++cursor;
    while (*cursor != 0U) {
        if (*cursor >= (u8)'a' && *cursor <= (u8)'z')
            mode = 0U;
        ++cursor;
    }
    return mode;
}

/* Recovered glyph-string writer at i960 0x0001da90. */
void recovered_text_write_glyph_string(volatile const u8 *text)
{
    u32 font_mode = recovered_text_string_font_mode((const u8 *)text);
    u8 character;

    while ((character = *text++) != 0U)
        recovered_text_emit_glyph(character, font_mode, 0U);
}

/* Describe one 0x1bc90 row transfer. */
u32 recovered_text_video_row_transfer_plan(
    u32 row,
    u32 source,
    u32 destination,
    u32 halfwords,
    u32 rows,
    u32 *call_source,
    u32 *call_destination,
    u32 *call_bytes)
{
    u32 row_bytes;

    if (row >= rows)
        return 0U;
    row_bytes = halfwords << 1;
    *call_source = source + (row << 7);
    *call_destination = destination + row * row_bytes;
    *call_bytes = row_bytes;
    return 1U;
}

/* Recovered 0x1bc90 row loop. */
void recovered_text_video_copy_rows(volatile u8 *source,
                                    volatile u8 *destination,
                                    u32 halfwords,
                                    u32 rows)
{
    u32 row;
    u32 row_bytes = halfwords << 1;

    for (row = 0U; row < rows; ++row) {
        recovered_memory_copy_forward(destination, source, row_bytes);
        source += 0x80U;
        destination += row_bytes;
    }
}

/* Describe the 0x20180 upload request before it enters the row blitter. */
u32 recovered_text_video_upload_plan(u32 *source,
                                    u32 *destination_pointer,
                                    u32 *halfwords,
                                    u32 *rows)
{
    *source = 0x01004000U;
    *destination_pointer = 0x02fd61d0U;
    *halfwords = 0x40U;
    *rows = 0x40U;
    return 1U;
}

/* Expand one source halfword as the 0x1bb90 converter does. */
u32 recovered_word_expand(u32 value)
{
    value &= 0xffffU;
    return ((value & 0x000fU) << 1)
        | ((value & 0x1000U) >> 12)
        | ((value & 0x00f0U) << 2)
        | ((value & 0x2000U) >> 8)
        | ((value & 0x0f00U) << 3)
        | ((value & 0x4000U) >> 4);
}

/* Recovered 16-word-block converter at i960 0x0001bb90. */
void recovered_word_expand_blocks(volatile u16 *destination,
                                  volatile const u16 *source,
                                  u32 blocks)
{
    u32 index;
    u32 words = blocks << 4;

    for (index = 0U; index < words; ++index)
        destination[index] = (u16)recovered_word_expand(source[index]);
}

u32 recovered_halfword_byte_swap(u32 value)
{
    value &= 0xffffU;
    return ((value & 0x00ffU) << 8) | ((value & 0xff00U) >> 8);
}

/* Recovered halfword byte-swap loop at i960 0x0001bc20. */
void recovered_halfword_byte_swap_copy(volatile u16 *destination,
                                       volatile const u16 *source,
                                       u32 halfwords)
{
    u32 index;

    for (index = 0U; index < halfwords; ++index)
        destination[index] = (u16)recovered_halfword_byte_swap(source[index]);
}

/* The first profile-zero startup transfer installs the font data consumed by
 * recovered_text_emit_glyph().  Its source, destination, and count are
 * preserved from the captured 0x1bc20 transfer descriptor. */
void recovered_text_font_asset_initialize(void)
{
    recovered_halfword_byte_swap_copy(
        (volatile u16 *)0x01081000U,
        (volatile const u16 *)0x02e21a74U,
        0x18800U);
}

/*
 * Describe one transfer selected by the 0x1bda0 startup asset loader.
 *
 * The original selects the zero profile only when g0 is zero; all nonzero
 * inputs select the alternate profile.  Units are 16-word blocks for WORD
 * EXPAND and halfwords for the other two kinds.  This is deliberately a
 * descriptor API: its ROM and hardware-RAM addresses are useful to tools,
 * while executing the mapped writes remains caller-owned.
 */
u32 recovered_text_startup_asset_transfer_plan(
    u32 profile,
    u32 index,
    u32 *kind,
    u32 *destination,
    u32 *source_or_value,
    u32 *units)
{
    struct recovered_startup_transfer transfer;
    u32 table_index;
    u32 first_table_count;
    u32 second_table_count;

    if (profile == 0U) {
        first_table_count = 3U;
        second_table_count = 3U;
    } else {
        first_table_count = 2U;
        second_table_count = 2U;
    }

    if (index < first_table_count + second_table_count) {
        u32 table = index & 1U;

        table_index = index >> 1;
        transfer.kind = RECOVERED_STARTUP_WORD_EXPAND;
        transfer.destination = 0x01800020U + (table << 12);
        while (table_index != 0U) {
            transfer.destination += (profile == 0U
                ? STARTUP_PROFILE_ZERO_BLOCKS[table_index - 1U]
                : STARTUP_PROFILE_NONZERO_BLOCKS[table_index - 1U]) << 5;
            --table_index;
        }
        table_index = index >> 1;
        if (profile == 0U) {
            transfer.source_or_value =
                STARTUP_PROFILE_ZERO_SOURCES[table][table_index];
            transfer.units = STARTUP_PROFILE_ZERO_BLOCKS[table_index];
        } else {
            transfer.source_or_value =
                STARTUP_PROFILE_NONZERO_SOURCES[table][table_index];
            transfer.units = STARTUP_PROFILE_NONZERO_BLOCKS[table_index];
        }
    } else {
        index -= first_table_count + second_table_count;
        if (index == 0U) {
            transfer.kind = RECOVERED_STARTUP_HALFWORD_SWAP;
            transfer.destination = 0x01081000U;
            transfer.source_or_value = 0x02e21a74U;
            transfer.units = 0x18800U;
        } else if (index == 1U) {
            transfer.kind = RECOVERED_STARTUP_HALFWORD_SWAP;
            transfer.destination = 0x010b2000U;
            transfer.source_or_value = profile == 0U ? 0x02e21054U : 0x02e4e0d4U;
            transfer.units = profile == 0U ? 0x17000U : 0x27000U;
        } else if (profile == 0U && index == 2U) {
            transfer.kind = RECOVERED_STARTUP_HALFWORD_SWAP;
            transfer.destination = 0x010e0000U;
            transfer.source_or_value = 0x02e6db14U;
            transfer.units = 0x6800U;
        } else {
            static const struct recovered_startup_transfer TAIL[] = {
                {RECOVERED_STARTUP_HALFWORD_SWAP, 0x010a9100U, 0x00144cc4U, 0x770U},
                {RECOVERED_STARTUP_HALFWORD_SWAP, 0x00ffb600U, 0x00146324U, 0x480U},
                {RECOVERED_STARTUP_HALFWORD_SWAP, 0x00ffa200U, 0x00144184U, 0x5a0U},
                {RECOVERED_STARTUP_HALFWORD_SWAP, 0x00ffe800U, 0x00145ba4U, 0x3c0U},
                {RECOVERED_STARTUP_HALFWORD_SWAP, 0x00286f80U, 0x00146c24U, 0x20U},
                {RECOVERED_STARTUP_HALFWORD_SWAP, 0x01086fc0U, 0x00146c64U, 0x20U},
                {RECOVERED_STARTUP_HALFWORD_FILL, 0x010aae00U, 0x9999U, 0x10U},
                {RECOVERED_STARTUP_WORD_EXPAND, 0x01801520U, 0x0001bb50U, 1U},
                {RECOVERED_STARTUP_WORD_EXPAND, 0x01801f40U, 0x0001bb70U, 1U},
                {RECOVERED_STARTUP_WORD_EXPAND, 0x01801f60U, 0x0001bb70U, 1U},
                {RECOVERED_STARTUP_WORD_EXPAND, 0x01801fc0U, 0x0001bb70U, 1U}
            };
            u32 tail_index = index - (profile == 0U ? 3U : 2U);

            if (tail_index >= (u32)(sizeof(TAIL) / sizeof(TAIL[0])))
                return 0U;
            transfer = TAIL[tail_index];
        }
    }

    *kind = transfer.kind;
    *destination = transfer.destination;
    *source_or_value = transfer.source_or_value;
    *units = transfer.units;
    return 1U;
}

/* Describe the fixed 0x1c730 request prepared by 0x1c220. */
u32 recovered_text_video_control_helper_plan(
    u32 *entry,
    u32 *source,
    u32 *destination,
    u32 *flags,
    u32 *count)
{
    *entry = 0x0001c730U;
    *source = 0x02ea0bb8U;
    *destination = 0x01080000U;
    *flags = 0x80U;
    *count = 1U;
    return 1U;
}

/*
 * Describe one direct bus/state write made by 0x1c220 before or after its
 * 0x1c730 and 0x1c618 calls.  The original carries its caller-provided g14
 * through these writes rather than materializing zero locally; expose that
 * value so the plan remains instruction-faithful.
 */
u32 recovered_text_video_control_write_plan(
    u32 index,
    u32 caller_g14,
    u32 *address,
    u32 *value,
    u32 *width)
{
    static const u32 ADDRESSES[10] = {
        0x00504d20U, 0x01040000U, 0x01060000U, 0x00504d34U,
        0x00504d38U, 0x00504ce4U, 0x00504ce0U, 0x00504cf4U,
        0x00504cf8U, 0x00504d10U
    };
    static const u32 WIDTHS[10] = {4U, 2U, 2U, 4U, 4U, 4U, 4U, 4U, 4U, 4U};

    if (index >= 10U)
        return 0U;
    *address = ADDRESSES[index];
    *width = WIDTHS[index];
    if (index == 0U)
        *value = 0x0001c2c0U;
    else if (index == 1U)
        *value = 0xffacU;
    else if (index == 2U)
        *value = 0xfffeU;
    else if (index == 9U)
        *value = 0U - 1U;
    else
        *value = caller_g14;
    return 1U;
}

/* Expand one source nibble into the four 4-bit lanes used by 0x1c730. */
static u32 recovered_text_expand_video_nibble(u32 nibble, u32 color)
{
    u32 expanded = 0U;

    if ((nibble & 8U) != 0U)
        expanded |= color << 12;
    if ((nibble & 4U) != 0U)
        expanded |= color << 8;
    if ((nibble & 2U) != 0U)
        expanded |= color << 4;
    if ((nibble & 1U) != 0U)
        expanded |= color;
    return expanded;
}

/* Recovered packed-byte to four-bit-lane expansion at i960 0x0001c730. */
u32 recovered_text_expand_video_byte(u32 source, u32 color)
{
    u32 high;
    u32 low;

    source &= 0xffU;
    color &= 0x0fU;
    high = recovered_text_expand_video_nibble(source >> 4, color);
    low = recovered_text_expand_video_nibble(source, color);
    return high | (low << 16);
}

/*
 * The original consumes and produces eight values per positive block count.
 * A zero count is not a valid original call, but is safely empty here.
 */
void recovered_text_expand_video_blocks(volatile u32 *destination,
                                        volatile const u8 *source,
                                        u32 blocks,
                                        u32 color)
{
    u32 index;
    u32 values = blocks << 3;

    for (index = 0U; index < values; ++index)
        destination[index] = recovered_text_expand_video_byte(source[index], color);
}

/* Recovered fixed video upload at i960 0x00020180. */
void recovered_text_video_upload(void)
{
    u32 source;
    u32 destination_pointer;
    u32 halfwords;
    u32 rows;
    u32 destination;

    recovered_text_video_upload_plan(&source, &destination_pointer,
                                     &halfwords, &rows);
    destination = *(volatile const u32 *)(unsigned long)destination_pointer;
    recovered_text_video_copy_rows((volatile u8 *)(unsigned long)source,
                                   (volatile u8 *)(unsigned long)destination,
                                   halfwords, rows);
}

/* Describe the 0x1d310 glyph-table and tile-address selection. */
u32 recovered_text_glyph_address_plan(
    u32 character,
    u32 font_mode,
    u32 column,
    u32 row,
    u32 *normalized_character,
    u32 *font_bank,
    u32 *glyph_descriptor,
    u32 *tile_address_first,
    u32 *tile_address_second)
{
    u32 character7 = character & 0x7fU;
    u32 normalized = 0U;
    u32 bank = font_mode & 3U;
    u32 tile = 0x01000000U + (((row << 6) + column) << 1);

    if (character7 >= 0x20U)
        normalized = character7 - 0x20U;
    *normalized_character = normalized;
    *font_bank = bank;
    *glyph_descriptor = GLYPH_TABLES[bank] + (normalized << 3);
    *tile_address_first = tile;
    *tile_address_second = tile + 0x80U;
    return 1U;
}

/* Describe one tile write selected by the 0x1d310 glyph loop. */
u32 recovered_text_glyph_tile_plan(
    u32 glyph_data,
    u32 width,
    u32 row,
    u32 column,
    u32 plane,
    u32 entry,
    u32 *glyph_word_address,
    u32 *tile_address)
{
    if (plane >= 2U || entry >= width)
        return 0U;
    *glyph_word_address = glyph_data + ((plane * width + entry) << 1);
    *tile_address = 0x01000000U
        + (((row << 6) + column + (plane << 6) + entry) << 1);
    return 1U;
}

u32 recovered_text_glyph_next_column(u32 normalized_character,
                                     u32 column,
                                     u32 width)
{
    if (normalized_character == 0x5cU)
        ++column;
    if (column <= 61U)
        column += width;
    return column;
}

/* Describe one fixed warning record from the 0x1674 interrupt sequence. */
u32 recovered_text_voltage_warning_plan(u32 index,
                                        u32 *column,
                                        u32 *row,
                                        u32 *text)
{
    if (index >= 4U)
        return 0U;
    *column = VOLTAGE_WARNING_COLUMNS[index];
    *row = VOLTAGE_WARNING_ROWS[index];
    *text = VOLTAGE_WARNING_TEXTS[index];
    return 1U;
}

/* Recovered glyph-table writer at i960 0x0001d310. */
void recovered_text_emit_glyph(u32 character, u32 font_mode, u32 attributes)
{
    u32 normalized;
    u32 bank;
    u32 descriptor;
    u32 first_tile;
    u32 second_tile;
    u32 width;
    u32 plane;
    u32 entry;
    u32 column = *TEXT_STATE_COLUMN;
    u32 row = *TEXT_STATE_ROW;
    volatile const u16 *glyph;

    recovered_text_glyph_address_plan(character, font_mode, column, row,
                                      &normalized, &bank, &descriptor,
                                      &first_tile, &second_tile);
    (void)bank;
    (void)first_tile;
    (void)second_tile;
    glyph = (volatile const u16 *)(unsigned long)
        *(volatile const u32 *)(unsigned long)descriptor;
    width = *(volatile const u32 *)(unsigned long)(descriptor + 4U);
    for (plane = 0U; plane < 2U; ++plane) {
        volatile u16 *tile = TILE_RAM + ((row + plane) << 6) + column;

        for (entry = 0U; entry < width; ++entry)
            tile[entry] = (u16)(*glyph++ | 0x8000U | attributes);
    }
    *TEXT_STATE_COLUMN = recovered_text_glyph_next_column(normalized, column,
                                                           width);
}

/* Pure description of the single bus write in the 0x1ccf8 helper. */
u32 recovered_text_tile_control_bus(u32 value, u32 *address)
{
    *address = 0x01800000U;
    return value;
}

/* Recovered text/tile control write at i960 0x0001ccf8. */
void recovered_text_write_tile_control(u32 value)
{
    TILE_CONTROL = value;
}

/* Describe the four halfword ranges cleared by the 0x1c618 initializer. */
u32 recovered_text_video_clear_plan(u32 index, u32 *address, u32 *halfwords)
{
    if (index >= 4U)
        return 0U;
    *address = VIDEO_CLEAR_ADDRESSES[index];
    *halfwords = VIDEO_CLEAR_HALWORDS[index];
    return 1U;
}

/* Describe the five initial state writes before the video clears. */
u32 recovered_text_video_state_plan(u32 index, u32 *address, u32 *value)
{
    if (index < 6U) {
        *address = 0x00504d24U + index * 2U;
        *value = 0U;
        return 1U;
    }
    if (index == 6U) {
        *address = 0x00504d32U;
        *value = 0x4000U;
        return 1U;
    }
    if (index == 7U) {
        *address = 0x00504d34U;
        *value = 0U;
        return 1U;
    }
    if (index == 8U) {
        *address = 0x00504d38U;
        *value = 0U;
        return 1U;
    }
    return 0U;
}

static void recovered_text_clear_video_region(u32 address, u32 halfwords)
{
    volatile u16 *destination = (volatile u16 *)(unsigned long)address;

    while (halfwords-- != 0U)
        *destination++ = 0U;
}

/* Recovered text/tile/video initialization at i960 0x0001c618. */
void recovered_text_video_initialize(void)
{
    u32 index;
    u32 address;
    u32 halfwords;
    u32 value;

    for (index = 0; index < 7U; ++index) {
        recovered_text_video_state_plan(index, &address, &value);
        *(volatile u16 *)(unsigned long)address = (u16)value;
    }
    *(volatile u32 *)0x00504d34 = 0U;
    *(volatile u32 *)0x00504d38 = 0U;

    for (index = 0; index < 4U; ++index) {
        recovered_text_video_clear_plan(index, &address, &halfwords);
        recovered_text_clear_video_region(address, halfwords);
    }
}

/* Recovered warning-message sequence at i960 0x00001674-0x000016d8. */
void recovered_text_voltage_warning_message_sequence(void)
{
    u32 index;
    u32 column;
    u32 row;
    u32 text;

    recovered_text_video_initialize();
    for (index = 0U; index < 4U; ++index) {
        recovered_text_voltage_warning_plan(index, &column, &row, &text);
        recovered_text_set_position(column, row);
        recovered_text_write_glyph_string(
            (volatile const u8 *)(unsigned long)text);
    }
}

/* Recovered bit-9 interrupt branch and its terminal fatal tail. */
void recovered_text_voltage_warning_interrupt_path(void)
{
    recovered_text_video_upload();
    recovered_text_voltage_warning_message_sequence();
    recovered_host_fatal_halt();
}
