/* Recovered finite path for the SHARC opcode-0x28 projected predicate. */
#include <math.h>
#include <stdint.h>

/*
 * The state window uses the established column-major affine convention.  All
 * three translated components are formed by the ROM; only the third
 * participates in the visible predicate.
 *
 * Inputs are (x,y,z), state[0..8] is the 3x3 matrix, state[9..11] is the
 * translation tail, and bounds are the fifth and sixth FIFO words (R5,R6).
 * The normal finite path accepts iff
 *   f2 > 0, f2 < upper, sqrt(x*x + z*f2) < f2*lower.
 */
static void recovered_sharc_opcode_28_project_impl(
    const float input[3], const float state[12], float projected[3])
{
    const float x = input[0];
    const float y = input[1];
    const float z = input[2];
    projected[0] = state[9] + x * state[0] + y * state[3] + z * state[6];
    projected[1] = state[10] + x * state[1] + y * state[4] + z * state[7];
    projected[2] = state[11] + x * state[2] + y * state[5] + z * state[8];
}

void recovered_sharc_opcode_28_project(
    const float input[3], const float state[12], float output[3])
{
    recovered_sharc_opcode_28_project_impl(input, state, output);
}

uint32_t recovered_sharc_opcode_28_accepts(
    const float input[3], const float state[12], float lower, float upper)
{
    const float x = input[0];
    const float z = input[2];
    float projected[3];
    recovered_sharc_opcode_28_project_impl(input, state, projected);
    const float depth = projected[2];
    const float radial = sqrtf(x * x + z * depth);
    const float scaled_bound = depth * lower;

    /*
     * The ROM's compare/branch sequence sends unordered results to the same
     * delayed zero return.  This is observable for both NaN depth and NaN
     * horizontal input; do not rely on C's unordered relational operators,
     * whose false/false result would otherwise accept the request.
     */
    if (!isfinite(depth) || !isfinite(radial) || !isfinite(scaled_bound) ||
        depth <= 0.0f || depth >= upper || radial >= scaled_bound)
        return 0U;
    return 1U;
}
