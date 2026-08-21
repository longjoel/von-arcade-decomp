typedef unsigned long u32;
typedef unsigned short u16;

/* Model 2B host work RAM.  The smoke test makes execution observable without
 * depending on the original game's I/O or coprocessor initialization. */
#define WORKRAM ((volatile u32 *)0x00500000)
#define TILERAM ((volatile u16 *)0x01000000)
#define WARNING_TABLE ((volatile unsigned char *)0x02EA2918)

static u32 tile_offset_for_line(u16 line)
{
    if (line == 0x000c)
        return 0x0316;
    if (line < 0x0010 || line > 0x0020 || (line & 1) != 0)
        return 0xffffffffUL;
    return 0x040a + ((u32)(line - 0x0010) / 2) * 0x80;
}

static u32 render_text_table(void)
{
    volatile const unsigned char *cursor = WARNING_TABLE;
    u32 records = 0;

    for (;;)
    {
        u16 id = (u16)cursor[0] | ((u16)cursor[1] << 8);
        u16 line = (u16)cursor[2] | ((u16)cursor[3] << 8);
        u32 tile_offset;
        u32 index = 0;

        cursor += 4;
        if (id == 0xffff && line == 0xffff)
            break;

        tile_offset = tile_offset_for_line(line);
        if (tile_offset == 0xffffffffUL)
            break;

        while (cursor[index] != '\0')
        {
            TILERAM[tile_offset + index] = (u16)(0x8000U | cursor[index]);
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
