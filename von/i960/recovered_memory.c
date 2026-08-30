/* Recovered forward-copy primitive at i960 0x000f5d40-0x000f5e80. */

typedef unsigned int u32;
typedef unsigned char u8;

/*
 * The original chooses aligned 16-, 8-, 4-, 2-, then 1-byte transfers.
 * Its observable contract is a forward non-overlap copy.
 */
void recovered_memory_copy_forward(volatile u8 *destination,
                                   volatile const u8 *source,
                                   u32 bytes)
{
    while (bytes-- != 0U)
        *destination++ = *source++;
}
