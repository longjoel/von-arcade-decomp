/* Recovered from i960 routine 0x00028548. */

typedef unsigned long u32;
typedef unsigned short u16;
typedef unsigned char u8;

#define TEXTURE_RAM0 ((volatile u16 *)0x11400000)
#define TEXTURE_RAM1 ((volatile u16 *)0x11401000)
#define TEXTURE_TABLE ((volatile const u8 *)0x02fb1d10)

void recovered_texture_initializer(void)
{
    u32 index;

    /* Two adjacent 127-entry ramps, values floor(index / 2). */
    for (index = 1; index <= 0x7f; ++index)
        TEXTURE_RAM0[index - 1] = (u16)(index >> 1);
    for (index = 1; index <= 0x7f; ++index)
        TEXTURE_RAM0[0x7f + index - 1] = (u16)(index >> 1);

    /* The i960 loop copies 0x2080 bytes as halfword stores. */
    for (index = 0; index <= 0x207f; ++index)
        TEXTURE_RAM1[index] = TEXTURE_TABLE[index];
}
