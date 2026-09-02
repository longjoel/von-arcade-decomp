/* Recovered byte-lane lookup for SHARC opcode 0x41. */
#include <stdint.h>

uint32_t recovered_sharc_opcode_41_address(uint32_t operand, uint32_t base)
{
    return base + (operand >> 2);
}

uint8_t recovered_sharc_opcode_41_extract(uint32_t operand, uint32_t word)
{
    return (uint8_t)(word >> ((operand & 3u) * 8u));
}
