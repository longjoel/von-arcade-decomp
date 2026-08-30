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

void recovered_text_emit_glyph(u32 character, u32 font_mode, u32 attributes);

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

/* Describe one 0x1bc90 row transfer without entering the hardware blitter. */
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
