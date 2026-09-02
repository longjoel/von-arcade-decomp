/* Recovered finite-seed bound lane of SHARC opcode 0x4d. */
#include <math.h>

/*
 * The first angle helper receives dy and sqrt(dx^2 + dz^2).  The later
 * reconstruction scales the two angle components by state constants 2 and
 * 1/3, then takes their Euclidean magnitude.  This models F9 for finite,
 * positive seeds; SHARC exceptional-value behavior remains a separate issue.
 */
float recovered_sharc_opcode_4d_refined_bound(
    float dx, float dy, float dz, float fourth_input)
{
    float seed = dx * dx + dz * dz;
    /* RSQRTS(0) enters the observed singular refinement path; overflow and
     * other non-finite seeds follow the same non-finite result path. */
    if (seed == 0.0f || !isfinite(seed))
        return NAN;
    float horizontal = sqrtf(seed);
    float total = sqrtf(seed + dy * dy);
    float cosine = horizontal / total;
    float sine = dy / total;
    float scaled_cosine = fourth_input * 2.0f * cosine;
    float scaled_sine = fourth_input * (1.0f / 3.0f) * sine;
    return sqrtf(scaled_cosine * scaled_cosine + scaled_sine * scaled_sine);
}
