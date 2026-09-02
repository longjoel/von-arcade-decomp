/* Recovered LZ-style decoder from i960 routine 0x00027e50. */

/* i960 words remain 32-bit when this source is compiled on an LP64 host. */
typedef unsigned int u32;
typedef unsigned short u16;
typedef unsigned char u8;

#define TEXTURE_RING ((volatile u8 *)0x00511bb0)
#define TEXTURE_FORMAT_TABLE ((volatile const u8 *)0x00027c50)
#define TEXTURE_STATUS ((volatile u32 *)0x00515080)

static int texture_use_secondary_bank(u32 output_index)
{
    u8 low = TEXTURE_FORMAT_TABLE[output_index & 0x1ffU];
    u8 high = TEXTURE_FORMAT_TABLE[(output_index >> 8) & 0x1feU];

    if (high == 1 || low == 1)
        return 1;
    if (high == 3 && low >= 3)
        return 1;
    if (low == 3 && high >= 4)
        return 1;
    if (high == 5 && low >= 5)
        return 1;
    if (low == 5 && high >= 6)
        return 1;
    if (high == 7 && low >= 7)
        return 1;
    if (low == 7 && high >= 8)
        return 1;
    if (high == 9 && low >= 9)
        return 1;
    if (low == 9 && high >= 10)
        return 1;
    return 0;
}

int recovered_texture_decompress(volatile const u8 *source,
                                 volatile u16 *primary,
                                 volatile u16 *secondary)
{
    u8 *ring = (u8 *)TEXTURE_RING;
    u32 flags = 0;
    u32 write_index = 0xfeeU;
    u32 output_index = 0;
    u32 copy_offset = 0;
    u32 copy_index = 0;
    u32 copy_remaining = 0;
    u32 output_count;
    u32 pair;
    u32 value;
    u32 output_word;
    u32 index;

    /* The ROM clears 0xfed bytes of its persistent ring storage. */
    *TEXTURE_STATUS = 0;
    for (index = 0; index < 0xfedU; ++index)
        ring[index] = 0;

    output_count = ((u32)source[0] << 24) |
        ((u32)source[1] << 16) | ((u32)source[2] << 8) | source[3];
    output_count >>= 1;
    source += 4;

    while (output_index < output_count)
    {
        output_word = 0;
        for (pair = 0; pair < 2; ++pair)
        {
            if (copy_remaining == 0)
            {
                flags >>= 1;
                if ((flags & 0x100U) == 0)
                    flags = (u32)*source++ | 0xff00U;

                if ((flags & 1U) == 0)
                {
                    value = *source++;
                    ring[write_index] = (u8)value;
                    write_index = (write_index + 1) & 0xfffU;
                }
                else
                {
                    u32 low = *source++;
                    u32 high = *source++;
                    copy_offset = ((high & 0xf0U) << 4) | low;
                    /* The first copied byte is emitted immediately; the loop
                     * counter therefore encodes the nibble plus two. */
                    copy_remaining = (high & 0x0fU) + 2U;
                    copy_index = 1;
                    value = ring[copy_offset];
                    ring[write_index] = (u8)value;
                    write_index = (write_index + 1) & 0xfffU;
                }
            }
            else
            {
                value = ring[(copy_offset + copy_index) & 0xfffU];
                ++copy_index;
                if (copy_remaining < copy_index)
                    copy_remaining = 0;
                ring[write_index] = (u8)value;
                write_index = (write_index + 1) & 0xfffU;
            }

            if (pair == 0)
                output_word = value & 0xffU;
            else
            {
                output_word |= (value & 0xffU) << 8;
                if (output_index < 0x60000U ||
                    !texture_use_secondary_bank(output_index))
                    *primary = (u16)output_word;
                else
                    *secondary = (u16)output_word;
                ++primary;
                ++secondary;
                ++output_index;
            }
        }
    }
    /* The alternate ROM exit returns a shared status latch.  The decoder
     * itself does not assign it; hardware/other code may raise it while the
     * stream is being expanded. */
    return (int)*TEXTURE_STATUS;
}
