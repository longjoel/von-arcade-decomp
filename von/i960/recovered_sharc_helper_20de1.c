/* Recovered plane interpolation performed by SHARC helper 0x20de1. */
#include <stdint.h>

typedef uint32_t u32;

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

/*
 * The sentinel branch compares the two independently computed products after
 * the e39 parallel assignment.  The subtraction is in F2 and the branch at
 * e3a is therefore equivalent to F9 == F14, including signed-zero equality.
 * Keep this at the register level: mapping these temporaries back to natural
 * point coordinates is not established by the trace.
 */
int recovered_sharc_helper_20de1_equality_tail(u32 f9_word, u32 f14_word)
{
    return bits_float(f9_word) == bits_float(f14_word);
}

/*
 * Reproduce the complete e32..e39 pre-branch schedule.  The four arguments
 * are inherited state, not point coordinates: F11, F13, and the old F14/F15.
 * F2 and F4 are overwritten before the comparison, so exposing them as
 * inputs would hide the actual continuation boundary.
 */
int recovered_sharc_helper_20de1_equality_schedule(
    u32 f11_word, u32 f13_word, u32 old_f14_word, u32 old_f15_word,
    u32 *f9_word, u32 *f14_word, u32 *f2_word)
{
    float f11 = bits_float(f11_word);
    float f13 = bits_float(f13_word);
    float old_f14 = bits_float(old_f14_word);
    float old_f15 = bits_float(old_f15_word);
    float f1 = f11 - old_f14;
    float f6 = f11 - old_f15;
    float f8 = f1 * f6;
    float f0 = f11 - f13;
    float f14 = f0 * f6;
    float f5 = f11 - f14;
    float f10 = f0 * f5;
    float f2 = f11 - old_f15;
    float f13_new = f2 * f5;
    float f4 = f11 - f13_new;
    float f9 = f2 * f4;
    float f15 = f2 * f4;

    (void)f8;
    (void)f10;
    (void)f15;
    f2 = f9 - f14;
    if (f9_word != 0)
        *f9_word = float_bits(f9);
    if (f14_word != 0)
        *f14_word = float_bits(f14);
    if (f2_word != 0)
        *f2_word = float_bits(f2);
    return recovered_sharc_helper_20de1_equality_tail(
        float_bits(f9), float_bits(f14));
}

/*
 * The twelve words are four three-component points.  The ROM constructs the
 * plane through P0, P2, and P3, then evaluates its missing y coordinate at the
 * caller's x/z pair (R8/R9).  Return 0 for a zero y-normal; that is the
 * degenerate case handled by the ROM's alternate tails.
 */
int recovered_sharc_helper_20de1_plane_y(const u32 record[12],
                                         float x, float z, u32 *result)
{
    float p0x = bits_float(record[0]);
    float p0y = bits_float(record[1]);
    float p0z = bits_float(record[2]);
    float ux = bits_float(record[6]) - p0x;
    float uy = bits_float(record[7]) - p0y;
    float uz = bits_float(record[8]) - p0z;
    float vx = bits_float(record[9]) - p0x;
    float vy = bits_float(record[10]) - p0y;
    float vz = bits_float(record[11]) - p0z;
    float nx = (uy * vz) - (uz * vy);
    float ny = (uz * vx) - (ux * vz);
    float nz = (ux * vy) - (uy * vx);
    if (ny == 0.0f)
        return 0;

    float plane_constant = (nx * p0x) + (ny * p0y) + (nz * p0z);
    float value = ((nx * x) + (nz * z) - plane_constant) / (-ny);
    *result = float_bits(value);
    return 1;
}

/* The same plane expression with the ROM's RECIPS/Newton division schedule. */
extern u32 recovered_sharc_opcode_35_divide(
    u32 previous_f0, u32 w0, u32 previous_f2, u32 w2, u32 w4, u32 w5);

int recovered_sharc_helper_20de1_plane_y_recips(const u32 record[12],
                                                float x, float z, u32 *result)
{
    float p0x = bits_float(record[0]);
    float p0y = bits_float(record[1]);
    float p0z = bits_float(record[2]);
    float ux = bits_float(record[6]) - p0x;
    float uy = bits_float(record[7]) - p0y;
    float uz = bits_float(record[8]) - p0z;
    float vx = bits_float(record[9]) - p0x;
    float vy = bits_float(record[10]) - p0y;
    float vz = bits_float(record[11]) - p0z;
    float nx = (uy * vz) - (uz * vy);
    float ny = (uz * vx) - (ux * vz);
    float nz = (ux * vy) - (uy * vx);
    if (ny == 0.0f)
        return 0;

    float plane_constant = (nx * p0x) + (ny * p0y) + (nz * p0z);
    float numerator = ((nx * x) + (nz * z)) - plane_constant;
    *result = recovered_sharc_opcode_35_divide(
        float_bits(numerator), 0x3f800000, 0, 0x3f800000, 0,
        float_bits(-ny));
    return 1;
}
