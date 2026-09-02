/* Semantic model of SHARC opcode-0x15 Y-axis row-pair rotation. */

#include <stdint.h>

typedef uint32_t u32;
static float f(u32 bits) { union { u32 b; float v; } x = { bits }; return x.v; }
static u32 b(float value) { union { u32 b; float v; } x; x.v = value; return x.b; }

void recovered_sharc_opcode_15_rotate_y(u32 sine_bits, u32 cosine_bits,
                                         const u32 matrix[9], u32 output[9])
{
    float s = f(sine_bits), c = f(cosine_bits);
    output[3] = matrix[3]; output[4] = matrix[4]; output[5] = matrix[5];
    for (unsigned row = 0; row < 3; ++row) {
        float x = f(matrix[row]);
        float z = f(matrix[6 + row]);
        output[row] = b(c * x + s * z);
        output[6 + row] = b(-s * x + c * z);
    }
}
