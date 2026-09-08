/* Recovered four-vector matrix transform for SHARC opcode 0x09.
 *
 * Grouping correction: the handler reads four CONSECUTIVE FIFO triplets
 * (words 3k..3k+2 form vector k), not lane-major regroups. Proven live by
 * the 07->09->1a->11 matrix compose: a cyclic-shift matrix maps the input
 * triplets to shifted triplets in place, which a lane regroup would have
 * scattered. The identified host caller still packs three lane quadwords,
 * so how those lanes map to geometric vectors is open; the SHARC-side
 * contract below is what the hardware executes. */
#include <stdint.h>

/* Interpret one of the four vectors consumed by the handler: three
 * consecutive input words starting at 3*vector. */
void recovered_sharc_opcode_09_state_vector(
    const float state[12], unsigned vector, float output[3])
{
    output[0] = state[vector * 3 + 0];
    output[1] = state[vector * 3 + 1];
    output[2] = state[vector * 3 + 2];
}

/* The handler consumes four consecutive (x,y,z) triplets and writes four
 * transformed triplets to state words 0..11 using the established
 * column-dot order (listing PM 0x201c4-0x20210; stores at 0x203-0x210 land
 * F5/F6/F7, F9/F10/F11, F13/F14/F15, F0/F1/F2 via the R5-R15/R0-R2
 * aliases). No translation tail enters any vector. Float rounding of the
 * multiply-add lattice is unpinned; exact-regime inputs (0/1 scalings and
 * permutations) reproduce live words bit-exactly under both engines. */
void recovered_sharc_opcode_09_transform(
    const float input[12], const float matrix[9], float output[12])
{
    for (unsigned vector = 0; vector < 4; ++vector) {
        float coordinates[3];
        recovered_sharc_opcode_09_state_vector(input, vector, coordinates);
        const float x = coordinates[0];
        const float y = coordinates[1];
        const float z = coordinates[2];
        output[vector * 3 + 0] = x * matrix[0] + y * matrix[3] + z * matrix[6];
        output[vector * 3 + 1] = x * matrix[1] + y * matrix[4] + z * matrix[7];
        output[vector * 3 + 2] = x * matrix[2] + y * matrix[5] + z * matrix[8];
    }
}
