/* Recovered elementwise matrix-scale service for SHARC opcode 0x2a. */
#include <stddef.h>

void recovered_sharc_opcode_2a_scale(float matrix[9], float scalar)
{
    for (size_t index = 0; index < 9; ++index)
        matrix[index] *= scalar;
}
