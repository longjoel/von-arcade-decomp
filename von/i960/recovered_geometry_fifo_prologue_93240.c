/* Float-prologue FIFO packet, i960 routine 0x00093240-0x000933ac.
 *
 * Decoded from von/build/disasm/vonj-maincpu.lst. A floating-point
 * prologue derives a float addend from g3, then the routine emits the
 * familiar 12-word packet to the host FIFO at 0x884000 and tail-calls
 * the already-recovered 0x8e310 packet tail, which is outside this
 * contract.
 *
 * Prologue: init = (g3 + 0xbfff) & 0xffff selects the arithmetic leg. The
 * value operated on is the existing float mailbox at 0x562530, not init:
 * the low leg subtracts the extended-real constant 0.2 and keeps it when
 * it is >= -30.0, otherwise it uses +30.0f; the high leg adds 0.2 and keeps
 * it when it is <= +30.0, otherwise it uses -30.0f. The stored result is a
 * float32 bit pattern. Keeping the mailbox argument explicit preserves the
 * stateful boundary instead of treating the selector-derived init as data.
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

u32 prologue_cell(u32 mailbox_bits, u32 high_leg)
{
    float mailbox = bits_to_float(mailbox_bits);
    double shifted = high_leg ? (double)mailbox + 0.2
                              : (double)mailbox - 0.2;

    if (high_leg)
        return shifted <= 30.0 ? float_to_bits((float)shifted)
                               : PROLOGUE_NEG30_BITS;
    return shifted >= -30.0 ? float_to_bits((float)shifted)
                            : PROLOGUE_POS30_BITS;
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

/*
 * Compose the routine-level flow at 0x93240.  mailbox_bits represents the
 * persistent [0x562530] cell and is updated before the packet's float add;
 * tail_args describes the arguments passed to the final 0x8e310 call.
 */
void fifo_prologue_run(u32 g0, u32 g1, u32 g2, u32 g3,
                       u32 *mailbox_bits, u32 mem5024e8,
                       u32 *words, prologue_tail_args *tail_args)
{
    u32 init = prologue_init(g3);
    u32 cell = prologue_cell(*mailbox_bits, init > 0x7ffeU);

    *mailbox_bits = cell;
    fifo_prologue_packet_build(fadd_bits(g0, cell), g1, g2, g3, words);
    fifo_prologue_tail_args(mem5024e8, tail_args);
}
