/* SHARC opcode-0x1a affine state-output service, truncating
 * (hardware/DRC) contract.
 *
 * The 1a handler accumulates one output column at a time over the
 * pointed 12-word record (3x3 row-major coefficients at offsets 0..8,
 * translation at 9..11): out[j] = T[j] + x*M[0,j] + y*M[1,j] + z*M[2,j].
 * Under bootstrap MODE1 = 0x18000 (TRUNCATE|RND32) every multiply and
 * add truncates toward zero at 32 bits. The DRC reproduces this
 * (live 07-load/1a compose drains 42e09999/4354eeee/43b67333 on a
 * discriminating matrix), while the interpreter rounds to nearest
 * (42e0999a/4354eeef/43b67333); recovered_sharc_opcode_1a.c pins the
 * interpreter rounding instead and is labeled as such.
 *
 * All arithmetic below is exact integer work on the decoded
 * significands (same technique as recovered_sharc_divide_03_04.c),
 * immune to host FP codegen. Contract: finite normal operands and
 * results; zero returns signed zero, denormal/inf/NaN falls back to
 * host floats and is outside the tested domain.
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

typedef struct {
    int sign;
    int exp;
    u32 sig;
} dec32;

static dec32 decode_norm(u32 bits)
{
    dec32 d;
    d.sign = (int)(bits >> 31);
    d.exp = (int)((bits >> 23) & 0xffU) - 127;
    d.sig = (bits & 0x7fffffU) | 0x800000U;
    return d;
}

static u32 pack_norm(int sign, int exp, u32 sig24)
{
    u32 field = (u32)(exp + 127);
    return ((u32)sign << 31) | (field << 23) | (sig24 & 0x7fffffU);
}

static int is_zero_bits(u32 b)
{
    return (b & 0x7fffffffU) == 0;
}

static int is_norm_bits(u32 b)
{
    u32 field = (b >> 23) & 0xffU;
    return field != 0 && field != 0xffU;
}

static u32 chop_mul(u32 a, u32 b)
{
    dec32 x, y;
    u64 prod;
    int exp;
    u32 sig24;
    if (is_zero_bits(a) || is_zero_bits(b))
        return ((a ^ b) & 0x80000000U);
    if (!is_norm_bits(a) || !is_norm_bits(b))
        return float_to_bits(bits_to_float(a) * bits_to_float(b));
    x = decode_norm(a);
    y = decode_norm(b);
    prod = (u64)x.sig * (u64)y.sig;
    exp = x.exp + y.exp;
    if (prod & ((u64)1 << 47)) {
        sig24 = (u32)(prod >> 24);
        exp += 1;
    } else {
        sig24 = (u32)(prod >> 23);
    }
    return pack_norm(x.sign ^ y.sign, exp, sig24);
}

/* Truncated add of finite normals: chop(a + b). Same integer datapath
 * as chop_sub in recovered_sharc_divide_03_04.c with the subtrahend
 * un-negated. */
static u32 chop_add(u32 a, u32 b)
{
    dec32 x, y;
    int sign;
    u64 big, small;
    int big_exp, gap;
    u64 acc;
    int top;
    u32 sig24;
    int exp;
    if (!is_norm_bits(a) || !is_norm_bits(b))
        return float_to_bits(bits_to_float(a) + bits_to_float(b));
    x = decode_norm(a);
    y = decode_norm(b);
    if (x.exp > y.exp || (x.exp == y.exp && x.sig >= y.sig)) {
        big = x.sig;
        big_exp = x.exp;
        small = y.sig;
        gap = x.exp - y.exp;
        sign = x.sign;
    } else {
        big = y.sig;
        big_exp = y.exp;
        small = x.sig;
        gap = y.exp - x.exp;
        sign = y.sign;
    }
    if (x.sign == y.sign) {
        acc = ((u64)big << 39) + (gap >= 64 ? 0 : ((u64)small << 39) >> gap);
    } else {
        if (gap >= 63) {
            /* The subtrahend is a nonzero fraction of an ulp, so
             * the magnitude drops by exactly one ulp toward zero.
             * (For gap <= 62 the general path below sees a nonzero
             * integer subtrahend and borrows the same ulp.) */
            if (big == 0x800000u)
                return pack_norm(sign, big_exp - 1, 0xffffffu);
            return pack_norm(sign, big_exp, (u32)big - 1);
        }
        /* big holds the larger magnitude by construction, so the
         * difference is exact and non-negative here. */
        acc = ((u64)big << 39) - (((u64)small << 39) >> gap);
        if (acc == 0)
            return 0;
    }
    if (acc == 0)
        return 0;
    top = 63;
    while (!(acc & ((u64)1 << top)))
        --top;
    if (top >= 23)
        sig24 = (u32)(acc >> (top - 23));
    else
        sig24 = (u32)(acc << (23 - top));
    exp = big_exp + top - 62;
    if (exp + 127 <= 0)
        return (u32)sign << 31;
    if (exp + 127 >= 255)
        return ((u32)sign << 31) | 0x7f800000U;
    return pack_norm(sign, exp, sig24);
}

/* Opcode 0x1a: out[j] = state[9+j] + v[0]*state[j] + v[1]*state[3+j]
 * + v[2]*state[6+j], every op truncated. */
void sharc_opcode_1a_affine_trunc(const u32 vector[3],
                                  const u32 state[12], u32 output[3])
{
    unsigned column;
    for (column = 0; column < 3; ++column) {
        u32 result = state[9 + column];
        result = chop_add(result, chop_mul(vector[0], state[column]));
        result = chop_add(result, chop_mul(vector[1], state[3 + column]));
        result = chop_add(result, chop_mul(vector[2], state[6 + column]));
        output[column] = result;
    }
}
