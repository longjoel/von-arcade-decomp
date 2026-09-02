/* Semantic model of SHARC opcode-0x16 Z-axis row-pair rotation. */

#include <stdint.h>

typedef uint32_t u32;
static float f(u32 bits) { union { u32 b; float v; } x = { bits }; return x.v; }
static u32 b(float value) { union { u32 b; float v; } x; x.v = value; return x.b; }

void recovered_sharc_opcode_16_rotate_z(u32 sine_bits, u32 cosine_bits,
                                         const u32 matrix[9], u32 output[9])
{
    float s = f(sine_bits), c = f(cosine_bits);
    output[6] = matrix[6]; output[7] = matrix[7]; output[8] = matrix[8];
    for (unsigned column = 0; column < 3; ++column) {
        float x = f(matrix[column]);
        float y = f(matrix[3 + column]);
        output[column] = b(c * x - s * y);
        output[3 + column] = b(s * x + c * y);
    }
}
