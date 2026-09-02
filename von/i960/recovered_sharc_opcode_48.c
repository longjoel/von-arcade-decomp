/* Recovered five-word state upload for SHARC opcode 0x48. */
#include <stdint.h>

/* FIFO R0..R4 are copied verbatim to DM 0x30157..0x3015b. */
void recovered_sharc_opcode_48_upload(const uint32_t input[5],
                                      uint32_t state[5])
{
    state[0] = input[0];
    state[1] = input[1];
    state[2] = input[2];
    state[3] = input[3];
    state[4] = input[4];
}
