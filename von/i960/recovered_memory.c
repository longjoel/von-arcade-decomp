/* Recovered memory primitives at i960 0x000f5d40-0x000f5f10. */

#include <stdint.h>

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

/* Overlap-aware sibling at 0xf5e80; preserves memmove direction semantics. */
void recovered_memory_copy_overlap(volatile u8 *destination,
                                   volatile const u8 *source,
                                   u32 bytes)
{
    uintptr_t destination_address = (uintptr_t)destination;
    uintptr_t source_address = (uintptr_t)source;

    if (destination_address > source_address &&
        destination_address - source_address < (uintptr_t)bytes) {
        while (bytes != 0U) {
            --bytes;
            destination[bytes] = source[bytes];
        }
        return;
    }
    recovered_memory_copy_forward(destination, source, bytes);
}

/* Fixed wrappers around the shared 0xf5d40 forward-copy leaf. */
void recovered_state_shift_77de0(volatile u8 *state_504d60,
                                 volatile const u8 *state_504f60,
                                 volatile u8 *state_504e60)
{
    recovered_memory_copy_forward(state_504d60, state_504f60, 0xf4U);
    recovered_memory_copy_forward(state_504e60, state_504d60, 0xf4U);
}

void recovered_state_shift_77e20(volatile u8 *state_504d60,
                                 volatile const u8 *state_504e60,
                                 volatile u8 *state_504e60_out,
                                 volatile const u8 *state_504f60)
{
    recovered_memory_copy_forward(state_504d60, state_504e60, 0xf4U);
    recovered_memory_copy_forward(state_504e60_out, state_504f60, 0xf4U);
}
