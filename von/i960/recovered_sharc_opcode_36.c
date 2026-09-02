/* Recovered translation-tail add and uniform matrix scale for opcode 0x36. */
#include <stdint.h>

/*
 * Opcode 0x36 resets the persistent matrix to identity, adds the three direct
 * float inputs to the existing translation tail, and scales every identity
 * element by R13.
 */
void recovered_sharc_opcode_36_update(
    const float prior_tail[3], const float translation_delta[3], float scalar,
    float matrix[9], float tail[3])
{
    tail[0] = prior_tail[0] + translation_delta[0];
    tail[1] = prior_tail[1] + translation_delta[1];
    tail[2] = prior_tail[2] + translation_delta[2];

    matrix[0] = scalar;
    matrix[1] = 0.0f;
    matrix[2] = 0.0f;
    matrix[3] = 0.0f;
    matrix[4] = scalar;
    matrix[5] = 0.0f;
    matrix[6] = 0.0f;
    matrix[7] = 0.0f;
    matrix[8] = scalar;
}
