/* Exact signature check recovered from the original i960 slice at 0x2040. */

#include <stdint.h>

/* Return one when the four-byte candidate is either accepted ROM signature. */
uint32_t recovered_rom_signature_compare_2040(const uint8_t candidate[4])
{
    static const uint8_t sega[4] = { 'S', 'E', 'G', 'A' };
    static const uint8_t s32a[4] = { 'S', '3', '2', 'A' };
    uint32_t sega_match = 1U;
    uint32_t s32a_match = 1U;
    uint32_t i;

    for (i = 0U; i < 4U; ++i) {
        sega_match &= (candidate[i] == sega[i]);
        s32a_match &= (candidate[i] == s32a[i]);
    }
    return sega_match | s32a_match;
}
