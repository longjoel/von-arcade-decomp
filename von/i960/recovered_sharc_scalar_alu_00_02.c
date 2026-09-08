/* SHARC scalar ALU: opcodes 0x00-0x02 (add/sub/mul), FIFO contracts.
 *
 * Handler PCs from the dispatch table at file 0x099 (SHARC
 * 0x20000-based): 0x00 -> 0x20133, 0x01 -> 0x2013b, 0x02 -> 0x20143.
 * Each reads two FIFO words, applies one single-precision op, and
 * publishes one word:
 *   133: F0 = F0 + F1    13b: F0 = F0 - F1    143: F0 = F0 * F1
 *
 * Live hardware probing (von/build/probe_sharc_opcode_00_02.lua,
 * von/build/probe_sharc_chop.lua) shows the export truncates: seven
 * one-ulp-discriminating trials (0.1+0.2, 0.3-0.1, 0.1*0.1,
 * 1.0+0.1) all return the chopped word, never round-to-nearest.
 * The model computes in double and chops the mantissa, matching a
 * low-32-bit store of the wide result. Inputs are exact float32
 * values, so double rounding cannot disturb the chop on the tested
 * domain; denormal/overflow/NaN export is untested and falls back
 * to round-to-nearest, documented in the test.
 */

typedef unsigned int u32;
typedef unsigned long long u64;

static float bits_to_float(u32 b)
{
    float f;
    __builtin_memcpy(&f, &b, 4);
    return f;
}

static u32 float_to_bits(float f)
{
    u32 b;
    __builtin_memcpy(&b, &f, 4);
    return b;
}

static u64 double_to_bits(double d)
{
    u64 q;
    __builtin_memcpy(&q, &d, 8);
    return q;
}

static u32 chop_double(double d)
{
    u64 q = double_to_bits(d);
    int sign = (int)(q >> 63);
    int exp = (int)((q >> 52) & 0x7ffU) - 896;
    u32 mant = (u32)((q & 0xfffffffffffffULL) >> 29);
    if (exp <= 0 || exp >= 255)
        return float_to_bits((float)d);
    return ((u32)sign << 31) | ((u32)exp << 23) | mant;
}

u32 sharc_scalar_fadd(u32 a, u32 b)
{
    return chop_double((double)bits_to_float(a) + (double)bits_to_float(b));
}

u32 sharc_scalar_fsub(u32 a, u32 b)
{
    return chop_double((double)bits_to_float(a) - (double)bits_to_float(b));
}

u32 sharc_scalar_fmul(u32 a, u32 b)
{
    return chop_double((double)bits_to_float(a) * (double)bits_to_float(b));
}
