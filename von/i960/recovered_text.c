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
