/* Semantic model of SHARC opcode-0x1a's affine state-output service. */

typedef unsigned int u32;

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

/*
 * The SHARC state stores the 3x3 coefficients row-major at offsets 0..8,
 * while the service accumulates one output column at a time: x*m[0,j] +
 * y*m[1,j] + z*m[2,j].  Tail offsets 9..11 are the affine translation.
 */
void recovered_sharc_opcode_1a_affine(const u32 vector[3],
                                      const u32 state[12], u32 output[3])
{
    float x = bits_float(vector[0]);
    float y = bits_float(vector[1]);
    float z = bits_float(vector[2]);

    for (unsigned column = 0; column < 3; ++column) {
        float result = bits_float(state[9 + column]);
        result += x * bits_float(state[column]);
        result += y * bits_float(state[3 + column]);
        result += z * bits_float(state[6 + column]);
        output[column] = float_bits(result);
    }
}
