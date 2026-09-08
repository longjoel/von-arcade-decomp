/* SHARC 40-bit floating-point core, exact integer-arithmetic port.
 *
 * Architectural contract from third_party/mame-master float40 work
 * (compute.hxx RECIPS seed table, sharcfloat40.h): 40-bit registers
 * hold sign + 8-bit exponent (bias 127) + 31-bit fraction, i.e. an
 * IEEE-32 word shifted left 8. ALU ops round-to-nearest in 40 bits;
 * narrowing to 32 bits chops the low 8 (the truncating export seen
 * on live hardware). Ops below take rnd32=false, truncate=false;
 * stores chop via f40_store.
 */

typedef unsigned int u32;
typedef unsigned long long u64;
typedef long long s64;

#define F40_FRACTION_BITS 31
#define F40_EXP_BIAS 127
#define F40_SIGN_MASK ((u64)1 << 39)

static u64 f40_from_ieee32(u32 bits)
{
    return ((u64)bits) << 8;
}

static u32 f40_to_ieee32(u64 raw)
{
    return (u32)(raw >> 8);
}

static unsigned f40_bit_length(u64 value)
{
    unsigned result = 0;
    while (value) {
        ++result;
        value >>= 1;
    }
    return result;
}

typedef struct {
    int negative;
    u64 significand;
    int shift;
} f40_value;

static f40_value f40_decode(u64 raw)
{
    f40_value out;
    unsigned exponent = (unsigned)((raw >> F40_FRACTION_BITS) & 0xffU);
    u32 fraction = (u32)(raw & 0x7fffffffULL);
    out.negative = (raw & F40_SIGN_MASK) != 0;
    if (exponent == 0) {
        out.significand = fraction;
        out.shift = -149;
    } else {
        out.significand = ((u64)1 << 31) | fraction;
        out.shift = (int)exponent - 127 - 31;
    }
    return out;
}

static u64 f40_encode(f40_value in, unsigned precision, int truncate)
{
    unsigned length;
    int exponent;
    u64 significand;
    unsigned exponent_field;
    u64 fraction;
    u64 result;
    if (in.significand == 0)
        return in.negative ? F40_SIGN_MASK : 0;
    length = f40_bit_length(in.significand);
    exponent = (int)(length - 1) + in.shift;
    if (length > precision) {
        unsigned dropped = length - precision;
        u64 remainder;
        significand = in.significand >> dropped;
        remainder = in.significand - (significand << dropped);
        if (!truncate) {
            u64 halfway = (u64)1 << (dropped - 1);
            if (remainder > halfway ||
                (remainder == halfway && (significand & 1)))
                ++significand;
        }
    } else {
        significand = in.significand << (precision - length);
    }
    if (significand == ((u64)1 << precision)) {
        significand >>= 1;
        ++exponent;
    }
    exponent_field = (unsigned)(exponent + F40_EXP_BIAS);
    fraction = (significand - ((u64)1 << (precision - 1))) << (32 - precision);
    result = ((u64)exponent_field << F40_FRACTION_BITS) | fraction;
    if (in.negative)
        result |= F40_SIGN_MASK;
    return result;
}

static f40_value f40_rounded_input(u64 raw, int rnd32, int truncate)
{
    f40_value in = f40_decode(raw);
    unsigned precision = rnd32 ? 24U : 32U;
    u64 enc = f40_encode(in, precision, truncate);
    return f40_decode(enc);
}

static u64 f40_add_raw(u64 x, u64 y, int rnd32, int truncate)
{
    f40_value left = f40_rounded_input(x, rnd32, truncate);
    f40_value right = f40_rounded_input(y, rnd32, truncate);
    unsigned precision = rnd32 ? 24U : 32U;
    f40_value larger, smaller;
    int distance;
    int result_shift;
    unsigned left_shift, right_shift;
    u64 left_magnitude, right_magnitude;
    int negative;
    u64 magnitude;
    if (left.significand == 0) {
        f40_value r = right;
        return f40_encode(r, precision, truncate);
    }
    if (right.significand == 0) {
        f40_value l = left;
        return f40_encode(l, precision, truncate);
    }
    larger = left;
    smaller = right;
    if (larger.shift < smaller.shift) {
        larger = right;
        smaller = left;
    }
    distance = larger.shift - smaller.shift;
    if (distance > (int)precision) {
        f40_value l = larger;
        return f40_encode(l, precision, truncate);
    }
    if (distance == (int)precision) {
        u64 significand = larger.significand;
        if (!truncate) {
            u64 halfway = (u64)1 << (precision - 1);
            int away = smaller.significand > halfway ||
                (smaller.significand == halfway && (significand & 1));
            if (away) {
                if (larger.negative == smaller.negative)
                    ++significand;
                else
                    --significand;
            }
        }
        {
            f40_value v;
            v.negative = larger.negative;
            v.significand = significand;
            v.shift = larger.shift;
            return f40_encode(v, precision, truncate);
        }
    }
    result_shift = (left.shift < right.shift) ? left.shift : right.shift;
    left_shift = (unsigned)(left.shift - result_shift);
    right_shift = (unsigned)(right.shift - result_shift);
    left_magnitude = left_shift < 64 ? left.significand << left_shift : 0;
    right_magnitude = right_shift < 64 ? right.significand << right_shift : 0;
    if (left.negative == right.negative) {
        negative = left.negative;
        magnitude = left_magnitude + right_magnitude;
    } else if (left_magnitude >= right_magnitude) {
        negative = left.negative;
        magnitude = left_magnitude - right_magnitude;
    } else {
        negative = right.negative;
        magnitude = right_magnitude - left_magnitude;
    }
    {
        f40_value v;
        v.negative = negative;
        v.significand = magnitude;
        v.shift = result_shift;
        return f40_encode(v, precision, truncate);
    }
}

static u64 f40_multiply_raw(u64 x, u64 y, int rnd32, int truncate)
{
    f40_value left = f40_rounded_input(x, rnd32, truncate);
    f40_value right = f40_rounded_input(y, rnd32, truncate);
    f40_value v;
    v.negative = left.negative != right.negative;
    v.significand = left.significand * right.significand;
    v.shift = left.shift + right.shift;
    return f40_encode(v, rnd32 ? 24U : 32U, truncate);
}

/* ALU ops: round-to-nearest, full 40-bit precision. */
static u64 f40_add(u64 x, u64 y)
{
    return f40_add_raw(x, y, 0, 0);
}

static u64 f40_sub(u64 x, u64 y)
{
    return f40_add_raw(x, y ^ F40_SIGN_MASK, 0, 0);
}

static u64 f40_mul(u64 x, u64 y)
{
    return f40_multiply_raw(x, y, 0, 0);
}

/* Narrowing store: chop the low 8 bits. */
static u32 f40_store(u64 raw)
{
    return f40_to_ieee32(raw);
}

/* RECIPS seed: 7-bit mantissa lookup, negated exponent. Table from
 * compute.hxx (hardware seed ROM model). */
static const u32 recips_seed_table[128] = {
    0x007f8000U, 0x007e0000U, 0x007c0000U, 0x007a0000U,
    0x00780000U, 0x00760000U, 0x00740000U, 0x00720000U,
    0x00700000U, 0x006f0000U, 0x006d0000U, 0x006b0000U,
    0x006a0000U, 0x00680000U, 0x00660000U, 0x00650000U,
    0x00630000U, 0x00610000U, 0x00600000U, 0x005e0000U,
    0x005d0000U, 0x005b0000U, 0x005a0000U, 0x00590000U,
    0x00570000U, 0x00560000U, 0x00540000U, 0x00530000U,
    0x00520000U, 0x00500000U, 0x004f0000U, 0x004e0000U,
    0x004c0000U, 0x004b0000U, 0x004a0000U, 0x00490000U,
    0x00470000U, 0x00460000U, 0x00450000U, 0x00440000U,
    0x00430000U, 0x00410000U, 0x00400000U, 0x003f0000U,
    0x003e0000U, 0x003d0000U, 0x003c0000U, 0x003b0000U,
    0x003a0000U, 0x00390000U, 0x00380000U, 0x00370000U,
    0x00360000U, 0x00350000U, 0x00340000U, 0x00330000U,
    0x00320000U, 0x00310000U, 0x00300000U, 0x002f0000U,
    0x002e0000U, 0x002d0000U, 0x002c0000U, 0x002b0000U,
    0x002a0000U, 0x00290000U, 0x00280000U, 0x00280000U,
    0x00270000U, 0x00260000U, 0x00250000U, 0x00240000U,
    0x00230000U, 0x00230000U, 0x00220000U, 0x00210000U,
    0x00200000U, 0x001f0000U, 0x001f0000U, 0x001e0000U,
    0x001d0000U, 0x001c0000U, 0x001c0000U, 0x001b0000U,
    0x001a0000U, 0x00190000U, 0x00190000U, 0x00180000U,
    0x00170000U, 0x00170000U, 0x00160000U, 0x00150000U,
    0x00140000U, 0x00140000U, 0x00130000U, 0x00120000U,
    0x00120000U, 0x00110000U, 0x00100000U, 0x00100000U,
    0x000f0000U, 0x000f0000U, 0x000e0000U, 0x000d0000U,
    0x000d0000U, 0x000c0000U, 0x000c0000U, 0x000b0000U,
    0x000a0000U, 0x000a0000U, 0x00090000U, 0x00090000U,
    0x00080000U, 0x00070000U, 0x00070000U, 0x00060000U,
    0x00060000U, 0x00050000U, 0x00050000U, 0x00040000U,
    0x00040000U, 0x00030000U, 0x00030000U, 0x00020000U,
    0x00020000U, 0x00010000U, 0x00010000U, 0x00000000U
};

static u64 f40_recips(u32 bits)
{
    u32 mantissa = bits & 0x7fffffU;
    u32 sign = bits & 0x80000000U;
    int unbiased = ((int)((bits >> 23) & 0xffU)) - 127;
    int res_exponent = -unbiased - 1;
    u32 res_mantissa = recips_seed_table[mantissa >> 16];
    u32 res_exp_field;
    if (res_exponent > 125 || res_exponent < -126)
        return (u64)(sign != 0) << 39;
    res_exp_field = (u32)(res_exponent + 127);
    return f40_from_ieee32(sign | (res_exp_field << 23) | res_mantissa);
}
