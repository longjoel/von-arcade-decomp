/* Recovered angular projection for SHARC opcode 0x25. */
#include <math.h>
#include <stdint.h>

/*
 * The ROM reads the packet as (y, x, z), normalizes the vector, and calls
 * helper 0x20d68 for two angular components. FIX behaves as a floor for
 * the observed signed results. The zero-horizontal case is deliberately
 * represented by the ROM's canonical NaN-to-FIX result.
 */
void recovered_sharc_opcode_25_projection(float x, float y, float z,
                                          uint32_t output[2])
{
    const float scale = 10430.0595703125f; /* 0x4622f83d, 32767 / pi */
    float horizontal = hypotf(y, z);
    float first = atan2f(x, horizontal);
    float second = -atan2f(y, z);
    int positive_pi_endpoint = (y == 0.0f && z < 0.0f);

    if (horizontal == 0.0f)
        output[0] = 0x80000000U;
    else
        output[0] = (uint32_t)(int32_t)floorf(first * scale);
    /* The ROM canonicalizes the negative pi endpoint to signed +32767. */
    output[1] = positive_pi_endpoint
        ? 0x00007fffU
        : (uint32_t)(int32_t)floorf(second * scale);
}
