/* Recovered fixed-source bridge and seeded table copy for opcode 0x3b. */
#include <stddef.h>
#include <stdint.h>

uint32_t recovered_sharc_opcode_3b_copy(
    uint32_t source_value, const uint32_t table[12], uint32_t destination[13],
    uint32_t *source_output, uint32_t *pointer_output)
{
    uint32_t address = (source_value >> 2) + 0x01400000U;

    *source_output = source_value;
    destination[0] = 0x05800b0bU;
    for (size_t index = 0; index < 12; ++index)
        destination[index + 1] = table[index];
    *pointer_output = address + 13U;
    return address;
}
