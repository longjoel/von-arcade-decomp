/* SHARC divide/residual services: opcodes 0x03 (quotient) and 0x04 (residual).
 *
 * The live dispatch table (DM 0x30000+opcode snapshot) routes 0x03 to
 * PM 0x2014b and 0x04 to PM 0x2015b (listing file offsets 0x14b/0x15b).
 * Each handler reads exactly two FIFO words (R0 = numerator,
 * R12 = denominator), sets R11 = 2.0, seeds F0 = RECIPS F12 with
 * R7 = R0 (numerator into F7), then runs three Goldschmidt correction
 * rounds (d = x*d, n = x*n, e = 2-d, repeated) and finishes
 * F0 = F0*F7 (quotient). The 0x04 handler additionally stashes
 * R2 = R12 (denominator into F2) and R1 = R7 (numerator bits into F1),
 * then forms F0 = F0*F2 (q*D) and F0 = F1-F0 (N - q*D). The same
 * schedule appears with three chained passes in the 3-operand
 * normalize path (a22-a41); the 2-operand divide handlers run a
 * single pass each. Bootstrap sets MODE1 = 0x18000 (TRUNCATE|RND32,
 * listing addr 0x080), so hardware truncates every intermediate
 * toward zero at 32 bits.
 *
 * Engine behavior, pinned by forced-FIFO probes (von/build/
 * probe_sharc_opcode_04{c,d,w,v}.lua):
 * - DRC reproduces the truncating hardware semantics exactly: 13/13
 *   divide and 20/20 residual words match this model bit-for-bit.
 * - The interpreter (compute.hxx FADD/FMUL) evaluates the same pass
 *   in host round-to-nearest floats, so its quotients sit up to one
 *   ulp above (e.g. 6/2 -> 0x40400000) and its residuals differ
 *   (e.g. (1.7,1/3) -> 0xb4000000 vs 0x34000000 here). MODE1_TRUNCATE
 *   is honored there only for infinity saturation. The interpreter
 *   words are therefore an emulator artifact, not hardware truth.
 *
 * All arithmetic below is exact integer work on the decoded
 * significands: immune to host FP codegen (a double-based chop was
 * observed to narrow to float ops under -O2 in this translation
 * unit), and bit-exact by construction. Contract: finite normal
 * operands; zero returns signed zero, denormal/inf/NaN falls back to
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

/* Decoded finite normal: 24-bit significand with hidden bit and the
 * standard unbiased exponent, so the value is
 * (sig / 2^23) * 2^exp. */
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

/* Truncated multiply of finite normals. */
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
        /* 48-bit product: drop 24, exponent compensates the extra bit. */
        sig24 = (u32)(prod >> 24);
        exp += 1;
    } else {
        sig24 = (u32)(prod >> 23);
    }
    return pack_norm(x.sign ^ y.sign, exp, sig24);
}

/* Truncated subtract of finite normals: chop(a - b). */
static u32 chop_sub(u32 a, u32 b)
{
    dec32 x, y;
    int sign;
    u64 big, small;
    int big_exp, gap;
    u64 diff;
    int top, shift;
    u32 sig24;
    int exp;
    if (!is_norm_bits(a) || !is_norm_bits(b))
        return float_to_bits(bits_to_float(a) - bits_to_float(b));
    x = decode_norm(a);
    y = decode_norm(b);
    /* Negate b, then add magnitudes with the larger first. The <<39
     * headroom keeps every exact bit: chop needs no sticky past the
     * top 24, and the worst-case magnitude sum stays under 2^64. */
    y.sign ^= 1;
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
        /* Same sign after negation means a,b had opposite signs:
         * magnitudes add. */
        diff = ((u64)big << 39) + (gap >= 64 ? 0 : ((u64)small << 39) >> gap);
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
        diff = ((u64)big << 39) - (((u64)small << 39) >> gap);
    }
    if (diff == 0)
        return 0;
    top = 63;
    while (!(diff & ((u64)1 << top)))
        --top;
    /* Truncate the low bits (chop toward zero) and rescale: the diff
     * holds value * 2^-(big_exp - 62), so the top 24 bits leave the
     * standard exponent big_exp + top - 62. */
    if (top >= 23)
        sig24 = (u32)(diff >> (top - 23));
    else
        sig24 = (u32)(diff << (23 - top));
    exp = big_exp + top - 62;
    if (exp + 127 <= 0)
        return (u32)sign << 31;
    if (exp + 127 >= 255)
        return ((u32)sign << 31) | 0x7f800000U;
    return pack_norm(sign, exp, sig24);
}

/* RECIPS seed table and formula, shared with recovered_sharc_float40.c
 * (hardware seed ROM model from compute.hxx). */
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

static u32 recips_seed(u32 bits)
{
    u32 mantissa = bits & 0x7fffffU;
    u32 sign = bits & 0x80000000U;
    int unbiased = ((int)((bits >> 23) & 0xffU)) - 127;
    int res_exponent = -unbiased - 1;
    u32 res_mantissa = recips_seed_table[mantissa >> 16];
    u32 res_exp_field;
    if (res_exponent > 125 || res_exponent < -126)
        return sign;
    res_exp_field = (u32)(res_exponent + 127);
    return sign | (res_exp_field << 23) | res_mantissa;
}

#define SHARC_TWO_BITS 0x40000000U

static u32 goldschmidt_pass(u32 num, u32 den)
{
    u32 x = recips_seed(den);
    u32 d = chop_mul(x, den);
    u32 n = chop_mul(x, num);
    int i;
    for (i = 0; i < 3; ++i) {
        u32 e = chop_sub(SHARC_TWO_BITS, d);
        d = chop_mul(e, d);
        n = chop_mul(e, n);
    }
    return n;
}

/* Opcode 0x03: quotient of a/b. */
u32 sharc_divide_q(u32 a, u32 b)
{
    return goldschmidt_pass(a, b);
}

/* Opcode 0x04: residual a - q*b with the service's own quotient. */
u32 sharc_divide_residual(u32 a, u32 b)
{
    u32 q = goldschmidt_pass(a, b);
    return chop_sub(a, chop_mul(q, b));
}
