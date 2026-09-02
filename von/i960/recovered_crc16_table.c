/* Recovered table checksum at i960 0x00003120. */

#include <stdint.h>

/*
 * The ROM's table at 0x2f20 is the 256-entry CRC-CCITT/0x1021 table.  The
 * routine itself keeps the accumulator in the same 32-bit layout as the
 * original code, including its nonstandard DEBDEB00 seed and final fold.
 */
uint32_t recovered_crc16_table(const uint8_t *data,
                               int32_t stride,
                               uint32_t count,
                               const uint16_t table[256])
{
    uint32_t state = 0xdebdeb00U;
    while (count != 0U) {
        uint32_t index = (state >> 24) & 0xffU;
        uint32_t byte = *data;
        state = ((state + byte) << 8) ^ ((uint32_t)table[index] << 16);
        data += stride;
        --count;
    }

    return (uint32_t)(int32_t)(int16_t)table[(state >> 24) & 0xffU] ^
        ((state << 8) >> 16);
}
