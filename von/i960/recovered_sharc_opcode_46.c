/* Recovered seven-word state upload for SHARC opcode 0x46. */
#include <stdint.h>

/*
 * The service uploads FIFO words R0..R6 to DM 0x30150..0x30156. F4 is
 * negated before its store, so XORing the sign bit preserves the SHARC
 * floating-point bit pattern, including signed zero and NaN payloads.
 */
void recovered_sharc_opcode_46_upload(const uint32_t input[7],
                                      uint32_t state[7])
{
    state[0] = input[0];
    state[1] = input[1];
    state[2] = input[2];
    state[3] = input[3];
    state[4] = input[4] ^ 0x80000000u;
    state[5] = input[5];
    state[6] = input[6];
}
