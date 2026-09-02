/* Recovered destination derivation and seeded 12-word table copy for 0x39. */
#include <stddef.h>
#include <stdint.h>

uint32_t recovered_sharc_opcode_39_copy(
    uint32_t input, const uint32_t table[12], uint32_t destination[13])
{
    uint32_t address = (input >> 2) + 0x01400000U;

    destination[0] = 0x05800b0bU;
    for (size_t index = 0; index < 12; ++index)
        destination[index + 1] = table[index];
    return address;
}
