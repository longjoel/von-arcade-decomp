/* Recovered normal path for SHARC opcode 0x27. */
#include <math.h>
#include <stdint.h>

/*
 * scale_x and scale_z are the retained R0/R2 values from opcode 0x26.
 * state[0], state[2], and state[3] are the uploaded X/Z origins and
 * threshold. The normal path is selected when the weighted magnitude is not
 * greater than the threshold. The GT fallback emits three zero words.
 */
uint32_t recovered_sharc_opcode_27_normalized_lanes(
    float x, float z, float scale_x, float scale_z, const float state[5],
    float output[3])
{
    float dx = state[0] - x;
    float dz = state[2] - z;
    float magnitude = sqrtf(scale_x * dx * dx + scale_z * dz * dz);
    /* The ROM's unordered compare path selects the same three-zero fallback
     * as an ordinary GT result; C's relational operators would otherwise
     * fall through on NaN. */
    if (!isfinite(magnitude) || !isfinite(state[3]) || magnitude > state[3]) {
        output[0] = 0.0f;
        output[1] = 0.0f;
        output[2] = 0.0f;
        return 0U;
    }

    output[0] = dx / magnitude;
    output[1] = dz / magnitude;
    output[2] = 1.0f;
    return 1U;
}

/*
 * Opcode 0x26 uploads the same five words later read by opcode 0x27. The
 * first and third words are aliased: they are both the X/Z origins in the
 * state window and the retained R0/R2 weights used by the distance test.
 * State words 1 and 4 are not consumed by the visible 0x27 path.
 */
uint32_t recovered_sharc_opcode_27_uploaded_state(
    float x, float z, const float uploaded[5], float output[3])
{
    return recovered_sharc_opcode_27_normalized_lanes(
        x, z, uploaded[0], uploaded[2], uploaded, output);
}
