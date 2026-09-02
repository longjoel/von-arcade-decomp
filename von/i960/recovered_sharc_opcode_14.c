/* Semantic model of SHARC opcode-0x14 X-axis row-pair rotation. */

#include <stdint.h>

typedef uint32_t u32;

static float bits_float(u32 bits)
{
    union { u32 bits; float value; } value;
    value.bits = bits;
    return value.value;
}

static u32 float_bits(float value)
{
    union { u32 bits; float value; } result;
    result.value = value;
    return result.bits;
}

void recovered_sharc_opcode_14_rotate_x(u32 sine_bits, u32 cosine_bits,
                                         const u32 matrix[9], u32 output[9])
{
    float sine = bits_float(sine_bits);
    float cosine = bits_float(cosine_bits);

    output[0] = matrix[0];
    output[1] = matrix[1];
    output[2] = matrix[2];
    for (unsigned column = 0; column < 3; ++column) {
        float row1 = bits_float(matrix[3 + column]);
        float row2 = bits_float(matrix[6 + column]);
        output[3 + column] = float_bits(cosine * row1 - sine * row2);
        output[6 + column] = float_bits(sine * row1 + cosine * row2);
    }
}
