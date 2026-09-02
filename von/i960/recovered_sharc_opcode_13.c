/* Semantic model of SHARC opcode-0x13 row-scaled 3x3 state writeback. */

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

void recovered_sharc_opcode_13_scale_rows(const u32 vector[3],
                                          const u32 matrix[9], u32 output[9])
{
    for (unsigned row = 0; row < 3; ++row) {
        float scale = bits_float(vector[row]);
        for (unsigned column = 0; column < 3; ++column) {
            float element = bits_float(matrix[row * 3 + column]);
            output[row * 3 + column] = float_bits(scale * element);
        }
    }
}
