/* Register-level packet reconstruction for the residual tail at 0xdf2f4. */

#include <stdint.h>
#include <string.h>
#include "recovered_float.h"

/*
 * Decimal host commands 28 and 27 dispatch to SHARC opcodes 0x1c and 0x1b.
 * Their results are consumed as follows:
 *
 *   g6 = object[+0x58] * opcode_1c_result
 *   g5 = object[+0x58] * object[+0x5c] * opcode_1b_result
 *
 * The two following decimal command-31 packets then use those values and the
 * selected vector's Z plus its affine-transformed Z. Each packet is the host
 * command word followed by the six endpoint words expected by SHARC 0x1f.
 */
uint32_t
recovered_geometry_residual_distance_requests(
    float object_scale_58,
    float object_scale_5c,
    float opcode_1c_result,
    float opcode_1b_result,
    float selected_z,
    float affine_z,
    uint32_t packets[14])
{
    float first_x = object_scale_58 * opcode_1c_result;
    float first_z = object_scale_58 * object_scale_5c * opcode_1b_result;

    packets[0] = 31U;
    packets[1] = recovered_float_to_bits(first_x);
    packets[2] = 0U;
    packets[3] = 0U;
    packets[4] = 0U;
    packets[5] = recovered_float_to_bits(first_z);
    packets[6] = 0U;

    packets[7] = 31U;
    packets[8] = recovered_float_to_bits(selected_z);
    packets[9] = 0U;
    packets[10] = 0U;
    packets[11] = 0U;
    packets[12] = recovered_float_to_bits(affine_z);
    packets[13] = 0U;
    return 14U;
}
