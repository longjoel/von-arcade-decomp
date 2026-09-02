/* Recovered base-address calculation for SHARC opcode 0x40. */
#include <stdint.h>

uint32_t recovered_sharc_opcode_40_base(uint32_t operand)
{
    return (operand << 16) + UINT32_C(0x01c00000);
}
