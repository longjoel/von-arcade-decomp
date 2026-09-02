/* Recovered four-word constant initializer for SHARC opcode 0x44. */
#include <stdint.h>

/*
 * The ROM writes these literal IEEE-754 words to DM 0x3015c..0x3015f.
 * Keeping the interface word-based preserves the exact 1/3 encoding used by
 * the SHARC image instead of silently replacing it with a host float literal.
 */
void recovered_sharc_opcode_44_initialize(uint32_t constants[4])
{
    constants[0] = 0x40000000u;
    constants[1] = 0x3eaaaaabu;
    constants[2] = 0x3f000000u;
    constants[3] = 0x40400000u;
}
