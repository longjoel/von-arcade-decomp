/* Proven normalized-direction portion of SHARC opcode 0x23. */

typedef unsigned int u32;

extern u32 recovered_sharc_rsqrts_seed(u32 bits);

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

static float rsqrt(float value)
{
    float estimate = bits_float(recovered_sharc_rsqrts_seed(float_bits(value)));
    for (int round = 0; round < 3; ++round) {
        float square = estimate * estimate;
        square = square * value;
        estimate = 0.5f * estimate;
        estimate = estimate * (3.0f - square);
    }
    return estimate;
}

/*
 * Opcode 0x23 normalizes the three FIFO components, then negates the Y lane
 * before entering its persistent-state update.  This function stops at that
 * proven boundary; the subsequent basis construction is caller/state
 * dependent and is intentionally not folded into the direction contract.
 */
void recovered_sharc_opcode_23_normalized_direction(const u32 input[3],
                                                    u32 output[3])
{
    float x = bits_float(input[0]);
    float y = bits_float(input[1]);
    float z = bits_float(input[2]);
    float squared = (x * x) + (y * y) + (z * z);
    if (squared == 0.0f) {
        output[0] = 0xffffffffU;
        output[1] = 0xffffffffU;
        output[2] = 0xffffffffU;
        return;
    }
    float scale = rsqrt(squared);
    output[0] = float_bits(x * scale);
    output[1] = float_bits(-(y * scale));
    output[2] = float_bits(z * scale);
}

/*
 * The state-writing tail constructs a Y-up frame whose third row is the
 * normalized input direction, then post-multiplies the existing 3x3 state
 * by that frame.  State words use the Model 2 column-major convention: rows
 * consumed by the affine transform are (0,3,6), (1,4,7), and (2,5,8).
 *
 * This intentionally covers the finite, non-degenerate path.  The original
 * routine's x=z=0 path propagates SHARC NaNs, which needs a separate exact
 * NaN payload model if callers require bit-for-bit failure behavior.
 */
void recovered_sharc_opcode_23_update_state(const u32 input[3],
                                             const u32 state[9],
                                             u32 output[9])
{
    float x = bits_float(input[0]);
    float y = bits_float(input[1]);
    float z = bits_float(input[2]);
    float squared = (x * x) + (y * y) + (z * z);
    float scale = rsqrt(squared);
    float nx = x * scale;
    float ny = y * scale;
    float nz = z * scale;
    float horizontal = rsqrt((nx * nx) + (nz * nz));
    float row0[3] = { nz * horizontal, 0.0f, -nx * horizontal };
    float row1[3] = {
        -nx * ny * horizontal,
        1.0f / horizontal,
        -nz * ny * horizontal,
    };
    float row2[3] = { nx, ny, nz };
    float frame[3][3] = {
        { row0[0], row0[1], row0[2] },
        { row1[0], row1[1], row1[2] },
        { row2[0], row2[1], row2[2] },
    };

    for (int row = 0; row < 3; ++row) {
        float old_row[3] = {
            bits_float(state[row]),
            bits_float(state[row + 3]),
            bits_float(state[row + 6]),
        };
        for (int column = 0; column < 3; ++column) {
            output[row + (column * 3)] = float_bits(
                (old_row[0] * frame[0][column]) +
                (old_row[1] * frame[1][column]) +
                (old_row[2] * frame[2][column]));
        }
    }
}
