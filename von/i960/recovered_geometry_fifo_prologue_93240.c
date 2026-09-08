/* Float-prologue FIFO packet, i960 routine 0x00093240-0x000933ac.
 *
 * Decoded from von/build/disasm/vonj-maincpu.lst. A floating-point
 * prologue derives a float addend from g3, then the routine emits the
 * familiar 12-word packet to the host FIFO at 0x884000 and tail-calls
 * the already-recovered 0x8e310 packet tail, which is outside this
 * contract.
 *
 * Prologue: init = (g3 + 0xbfff) & 0xffff. As extended-real, init is
 * shifted by -0.05 (init <= 0x7ffe) or +0.05 (init > 0x7ffe) using the
 * double 0x3fc999999999999a, rounded back to integer, and compared:
 * - Low leg compares against the double -30.0 formed by the r4/r5
 *   pair (0, 0xc03e0000). Since init - 0.05 >= -0.05 > -30.0 always,
 *   the +30.0f fallback (0x41f00000) is unreachable and the leg
 *   keeps the rounded integer.
 * - High leg compares against the double +30.0 (pair (0, 0x403e0000));
 *   init + 0.05 > 30.0 always, so it always takes the -30.0f fallback
 *   (0xc1f00000).
 * In short the cell takes init's integer bits (low leg) or -30.0f
 * (high leg). The integer-to-float roundings are exact (small
 * integers) and init +/- 0.05 never lands on a halfway case, so the
 * i960 rounding mode cannot change the result; round-to-nearest-even
 * is assumed and documented.
 * The cell is stored to [0x562530] (a mailbox read only here), then
 * reloaded and added to g0 with a real (float32) add for packet w2.
 *
 * Packet: the standard 12-word template with a float sum in w2:
 * w = [5, 18, g0 + cell (float32), g1, g2, 21, g3 & 0xffff, 19,
 * 0x3e4ccccd x3, 6]. The [0x5024e8] word is never stored; it is only
 * reduced by unsigned `remo 30` for the tail call: a0 = 0x02b4b652,
 * a1 = a0 + 0x97512, a2 = mem % 30. Incoming g1/g2 are stored before
 * g2 is clobbered by the remainder.
 *
 * Observed caller goldens (three sites pass g3 = 0, hence the high
 * leg with cell -30.0f):
 * 0x969a4: g0 = 0, g1 = 0x41b40000, g2 = 0xc195999a.
 * 0x97150/0x97210: g0 = 0, g1 = 0x41b4cccd, g2 = 0xc19a6666.
 */

typedef unsigned int u32;

#include <math.h>

#define PROLOGUE_NEG30_BITS 0xc1f00000U
#define PROLOGUE_POS30_BITS 0x41f00000U
#define PACKET_FILL_CONST 0x3e4ccccdU
#define PACKET_WORDS 12U
#define TAIL_CALL_A0 0x02b4b652U
#define TAIL_CALL_A1_OFF 0x97512U

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

u32 prologue_init(u32 g3)
{
    return (g3 + 0xbfffU) & 0xffffU;
}

u32 prologue_cell(u32 init)
{
    double shifted;
    int rounded;
    if (init > 0x7ffeU)
        return PROLOGUE_NEG30_BITS;
    shifted = (double)(int)init - 0.05;
    rounded = (int)nearbyint(shifted);
    if ((double)rounded >= -30.0)
        return (u32)rounded;
    return PROLOGUE_POS30_BITS;
}

u32 fadd_bits(u32 a, u32 b)
{
    return float_to_bits(bits_to_float(a) + bits_to_float(b));
}

void fifo_prologue_packet_build(u32 g0sum, u32 g1, u32 g2, u32 g3,
                                u32 *words)
{
    words[0] = 5U;
    words[1] = 18U;
    words[2] = g0sum;
    words[3] = g1;
    words[4] = g2;
    words[5] = 21U;
    words[6] = g3 & 0xffffU;
    words[7] = 19U;
    words[8] = PACKET_FILL_CONST;
    words[9] = PACKET_FILL_CONST;
    words[10] = PACKET_FILL_CONST;
    words[11] = 6U;
}

typedef struct {
    u32 a0, a1, a2;
} prologue_tail_args;

void fifo_prologue_tail_args(u32 mem5024e8, prologue_tail_args *o)
{
    o->a0 = TAIL_CALL_A0;
    o->a1 = TAIL_CALL_A0 + TAIL_CALL_A1_OFF;
    o->a2 = mem5024e8 % 30U;
}
