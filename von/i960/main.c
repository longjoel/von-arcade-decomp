typedef unsigned long u32;
typedef unsigned short u16;
typedef unsigned char u8;

/* Model 2B host work RAM.  The smoke test makes execution observable without
 * depending on the original game's I/O or coprocessor initialization. */
#define WORKRAM ((volatile u32 *)0x00500000)
#define TILERAM ((volatile u16 *)0x01000000)
#define WARNING_TABLE ((volatile unsigned char *)0x02EA2918)

static u32 tile_offset_for_record(u16 column, u16 row)
{
    return ((u32)row << 6) + column;
}

static void advance_text_control(u8 character, u16 origin, u16 *column, u16 *row)
{
    if (character == '\t')
    {
        *column = (u16)((*column + 8) & ~7U);
        if (*column > 61)
        {
            *column = 0;
            if (*row <= 46)
                *row = (u16)(*row + 1);
        }
    }
    else if (character == '\n')
    {
        *column = origin;
        if (*row <= 46)
            *row = (u16)(*row + 1);
    }
}

static u32 render_text_table(void)
{
    volatile const unsigned char *cursor = WARNING_TABLE;
    u32 records = 0;

    for (;;)
    {
        u16 id = (u16)cursor[0] | ((u16)cursor[1] << 8);
        u16 line = (u16)cursor[2] | ((u16)cursor[3] << 8);
        u16 column = id;
        u32 index = 0;

        cursor += 4;
        if (id == 0xffff && line == 0xffff)
            break;

        while (cursor[index] != '\0')
        {
            u8 character = cursor[index];

            if (character <= 31)
                advance_text_control(character, id, &column, &line);
            else
            {
                TILERAM[tile_offset_for_record(column, line)] =
                    (u16)(0x8000U | character);
                if (column <= 61)
                    column++;
            }
            index++;
        }
        cursor += index + 1;
        records++;
    }

    return records;
}

void i960_prototype_main(void)
{
    volatile u32 *const marker = WORKRAM;

    *marker = 0x49393630UL;
    marker[1] = 0x50524F54UL;
    marker[2] = marker[2] + 1;
    marker[5] = render_text_table();
    marker[4] = 0x54455854UL;

    for (;;)
        marker[3] = marker[3] + 1;
}
