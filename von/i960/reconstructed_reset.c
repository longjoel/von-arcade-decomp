/* C reconstruction of the bounded i960 reset routine at ROM 0x930. */
#include <stdint.h>

typedef uint32_t u32;

void reconstructed_reset_entry(void)
{
    volatile const u32 *table_source =
        (volatile const u32 *)(uintptr_t)UINT32_C(0x000008f0);
    volatile u32 *table_destination =
        (volatile u32 *)(uintptr_t)UINT32_C(0x00e00000);
    u32 value;
    volatile u32 *copy_destination;
    volatile const u32 *copy_source;
    u32 copy_end;

    do
    {
        value = *table_source++;
        if (value == UINT32_MAX)
            break;
        *table_destination++ = value;
    } while (1);

    copy_destination = (volatile u32 *)(uintptr_t)UINT32_C(0x00501800);
    copy_source = (volatile const u32 *)(uintptr_t)UINT32_C(0x000000b0);
    copy_end = *(volatile const u32 *)(uintptr_t)UINT32_C(0x005018b0);
    while ((uintptr_t)copy_destination < (uintptr_t)copy_end)
        *copy_destination++ = *copy_source++;

    copy_destination = (volatile u32 *)(uintptr_t)UINT32_C(0x005018b0);
    copy_source = (volatile const u32 *)(uintptr_t)UINT32_C(0x00001c20);
    copy_end = *(volatile const u32 *)(uintptr_t)UINT32_C(0x00501cb4);
    while ((uintptr_t)copy_destination < (uintptr_t)copy_end)
        *copy_destination++ = *copy_source++;

    *(volatile u32 *)(uintptr_t)UINT32_C(0x00501814) =
        UINT32_C(0x005018b0);
    /* The original finishes with synmovq before ret.  It remains a separate
     * machine-control instruction until its C/compiler representation is
     * established. */
}
