/* C reconstruction of the bounded i960 reset routine at ROM 0x930. */
typedef unsigned long u32;

void reconstructed_reset_entry(void)
{
    volatile const u32 *table_source = (volatile const u32 *)0x000008f0UL;
    volatile u32 *table_destination = (volatile u32 *)0x00e00000UL;
    u32 value;
    volatile u32 *copy_destination;
    volatile const u32 *copy_source;
    u32 copy_end;

    do
    {
        value = *table_source++;
        if (value == 0xffffffffUL)
            break;
        *table_destination++ = value;
    } while (1);

    copy_destination = (volatile u32 *)0x00501800UL;
    copy_source = (volatile const u32 *)0x000000b0UL;
    copy_end = *(volatile const u32 *)0x005018b0UL;
    while ((u32)copy_destination < copy_end)
        *copy_destination++ = *copy_source++;

    copy_destination = (volatile u32 *)0x005018b0UL;
    copy_source = (volatile const u32 *)0x00001c20UL;
    copy_end = *(volatile const u32 *)0x00501cb4UL;
    while ((u32)copy_destination < copy_end)
        *copy_destination++ = *copy_source++;

    *(volatile u32 *)0x00501814UL = 0x005018b0UL;
    /* The original finishes with synmovq before ret.  It remains a separate
     * machine-control instruction until its C/compiler representation is
     * established. */
}
