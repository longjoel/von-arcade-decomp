typedef unsigned long u32;
typedef unsigned short u16;

/* Model 2B host work RAM.  The smoke test makes execution observable without
 * depending on the original game's I/O or coprocessor initialization. */
#define WORKRAM ((volatile u32 *)0x00500000)
#define TILERAM ((volatile u16 *)0x01000000)

struct warning_record
{
    u16 id;
    u16 line;
    const char *text;
    u32 tile_offset;
};

static const struct warning_record warning_records[] = {
    {0x0016, 0x000c, "W A R N I N G", 0x0316},
    {0x000a, 0x0010, "THIS GAME IS TO BE USED ONLY IN JAPAN.", 0x040a},
    {0x000a, 0x0012, "EXPORT, SALES, DISTRIBUTION AND/OR", 0x048a},
    {0x000a, 0x0014, "OPERATION OUTSIDE THIS AREA MAY", 0x050a},
    {0x000a, 0x0016, "CONSTITUTE A VIOLATION OF INTERNATIONAL", 0x058a},
    {0x000a, 0x0018, "LAWS ON COPYRIGHTS AND/OR INDUSTRIAL", 0x060a},
    {0x000a, 0x001a, "PROPERTY RIGHTS AND SUBJECT THE", 0x068a},
    {0x000a, 0x001c, "VIOLATING PARTY TO LEGAL PROCEEDINGS.", 0x070a},
    {0x000a, 0x0020, "                   SEGA ENTERPRISES,LTD.", 0x080a},
};

static void render_warning(void)
{
    u32 record;

    for (record = 0; record < sizeof(warning_records) / sizeof(warning_records[0]); record++)
    {
        const struct warning_record *entry = &warning_records[record];
        const char *text = entry->text;
        u32 index = 0;

        while (text[index] != '\0')
        {
            TILERAM[entry->tile_offset + index] = (u16)(0x8000U | (unsigned char)text[index]);
            index++;
        }
    }
}

void i960_prototype_main(void)
{
    volatile u32 *const marker = WORKRAM;

    *marker = 0x49393630UL;
    marker[1] = 0x50524F54UL;
    marker[2] = marker[2] + 1;
    render_warning();
    marker[4] = 0x54455854UL;

    for (;;)
        marker[3] = marker[3] + 1;
}
