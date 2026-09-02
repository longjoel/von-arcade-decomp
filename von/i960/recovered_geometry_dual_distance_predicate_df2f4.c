/* Final strict residual-distance predicate recovered from i960 0xdf2f4. */

#include <stdint.h>

/*
 * The two preceding host command-31 requests return floating-point lengths
 * from SHARC opcode 0x1f. At 0xdf380 the i960 performs CMPR(first, second)
 * followed by BGE to the reject path, so equality and greater-than reject.
 * NaN also fails the strict less-than acceptance condition.
 */
uint32_t recovered_geometry_dual_distance_accepts(float first_distance,
                                                  float second_distance)
{
    return first_distance < second_distance ? 1U : 0U;
}
