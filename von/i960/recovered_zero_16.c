/* Exact 16-byte clear helper at i960 0xc5d48. */

#include <stdint.h>

void recovered_zero_16(uint8_t bytes[16])
{
    uint32_t index;

    for (index = 0; index < 16; ++index)
        bytes[index] = 0;
}
