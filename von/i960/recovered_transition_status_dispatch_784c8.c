/* Status predicate dispatcher recovered from i960 0x784c8-0x7863c. */

#include <stdint.h>

/*
 * The original arms only conditionally write 1 to 0x504d84 and return
 * through their saved continuation.  Return the write decision, leaving the
 * persistent status cell and the continuation ABI to the caller.
 */
uint32_t recovered_transition_status_should_set_784c8(uint32_t selector,
                                                       uint32_t mode_bits)
{
    switch (selector) {
    case 0U:
    case 6U:
        return (mode_bits & 0x2U) != 0U;
    case 1U:
    case 3U:
        return (mode_bits & 0x4U) != 0U;
    case 2U:
    case 4U:
    case 5U:
    case 7U:
    case 8U:
    case 9U:
        return (mode_bits & 0x6U) != 0U;
    default:
        return 0U;
    }
}
