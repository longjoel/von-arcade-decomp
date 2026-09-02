/* Semantic model of SHARC opcode-0x12 matrix-vector tail accumulation. */

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

void recovered_sharc_opcode_12_accumulate(const u32 vector[3],
                                          const u32 matrix[9],
                                          const u32 tail[3], u32 output[3])
{
    for (unsigned column = 0; column < 3; ++column) {
        float value = bits_float(tail[column]);
        for (unsigned row = 0; row < 3; ++row)
            value += bits_float(vector[row]) * bits_float(matrix[row * 3 + column]);
        output[column] = float_bits(value);
    }
}
