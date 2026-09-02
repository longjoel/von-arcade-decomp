/* Recovered four-vector matrix transform for SHARC opcode 0x09. */
#include <stdint.h>

/* Interpret one of the four vectors encoded by the state-readback layout.
 * The state window is stored lane-major: [x0..x3,y0..y3,z0..z3].  When the
 * window is the usual row-major matrix plus tail, these are not necessarily
 * geometric vertices; they are the four triples induced by that wire layout. */
void recovered_sharc_opcode_09_state_vector(
    const float state[12], unsigned vector, float output[3])
{
    output[0] = state[vector];
    output[1] = state[4 + vector];
    output[2] = state[8 + vector];
}

/* The handler consumes four (x,y,z) triplets and writes four transformed
 * triplets to state words 0..11 using the established column-dot order.
 * The FIFO input is lane-major when supplied by the identified host caller:
 * [x0,x1,x2,x3,y0,y1,y2,y3,z0,z1,z2,z3]. */
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
