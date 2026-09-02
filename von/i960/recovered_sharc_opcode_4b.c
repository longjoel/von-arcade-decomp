/* Recovered finite-path predicate for SHARC opcode 0x4b. */
#include <math.h>
#include <stdint.h>

/*
 * Opcode 0x4b shares its normal arithmetic block with opcode 0x4d.  The
 * fourth input is the bound scale; state[3] is the additive bound term.
 * This intentionally models finite normal inputs only: SHARC RSQRTS
 * rounding and exceptional-value behavior remain separate concerns.
 */
uint32_t recovered_sharc_opcode_4b_predicate(float dx, float dy, float dz,
                                              float fourth_input,
                                              const float state[9])
{
    if (dy > 0.0f)
        return 1U;

    float horizontal_seed = dx * dx + dz * dz;
    /* The shared first RSQRTS path is singular for zero horizontal length;
     * the observed normal tail rejects with result 2. */
    if (horizontal_seed == 0.0f || isnan(horizontal_seed))
        return 2U;
    float horizontal = sqrtf(horizontal_seed);
    float radius = sqrtf(horizontal * horizontal + dy * dy);
    float cosine = horizontal / radius;
    float sine = dy / radius;
    float scaled_cosine = fourth_input * 2.0f * cosine;
    float scaled_sine = fourth_input * (1.0f / 3.0f) * sine;
    float refined_bound = sqrtf(scaled_cosine * scaled_cosine +
                                 scaled_sine * scaled_sine);
    return radius < refined_bound + state[3] ? 0U : 2U;
}
