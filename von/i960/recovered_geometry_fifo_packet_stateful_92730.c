/* Stateful geometry FIFO command packet, i960 routines
 * 0x00092730-0x00092824 and 0x000933b0-0x000934a4.
 *
 * The two routines share one logic template and differ only in their
 * RAM cells (0x92730: 0x5624a8/0x5624f0; 0x933b0: 0x5624ac/0x5624f4),
 * which arrive here as values, so one model covers both.
 *
 * Decoded from von/build/disasm/vonj-maincpu.lst. Emits a 13-word
 * packet to the host FIFO at 0x884000, then tail-calls the
 * already-recovered 0x8e310 packet tail, which is outside this
 * contract:
 *   w = [5, 44 (addo 31,13), g0, g1, g2, g14, g3 & 0xffff, g14,
 *        19, 0x3e4ccccd x3, 6].
 * Between the third fill word and the tail call, a 1-bit counter in
 * the F cell updates: when the A cell is zero, the 0xf5058 subroutine
 * runs (outside this contract; its effect on g0 arrives as an input)
 * and, if bit 0 of g0 is then set, F = (F + 1) & 1. The tail-call
 * args are a0 = 0x02b53ca2 plus 0xffffbc7e iff the updated F cell is
 * nonzero, a1 = 0x02be2b64, a2 = A cell.
 *
 * Observed caller goldens (packet w2/w3/w4/w6):
 * 0x968a0 -> 0x92730: g0 = 0xc12ccccd, g1 = 0x4227999a,
 *   g2 = 0x3f800000, g3 = 0x1500.
 * 0x968c4 -> 0x933b0: g0 = 0xc1066666, g1 = 0x42293333,
 *   g2 = 0x3fe66666, g3 = 0xffffa000.
 * (g14 is caller context and stays a free input.)
 */

typedef unsigned int u32;

#define STATEFUL_PACKET_WORDS 13U
#define STATEFUL_FILL_CONST 0x3e4ccccdU
#define STATEFUL_CALL_BASE 0x02b53ca2U
#define STATEFUL_CALL_ADJ 0xffffbc7eU
#define STATEFUL_CALL_A1 0x02be2b64U

void fifo_packet_stateful_build(u32 g0, u32 g1, u32 g2, u32 g3, u32 g14,
                                u32 *words)
{
    words[0] = 5U;
    words[1] = 44U;
    words[2] = g0;
    words[3] = g1;
    words[4] = g2;
    words[5] = g14;
    words[6] = g3 & 0xffffU;
    words[7] = g14;
    words[8] = 19U;
    words[9] = STATEFUL_FILL_CONST;
    words[10] = STATEFUL_FILL_CONST;
    words[11] = STATEFUL_FILL_CONST;
    words[12] = 6U;
}

u32 fifo_packet_stateful_toggle(u32 memA, u32 post_bal_g0, u32 memF)
{
    if (memA == 0U && (post_bal_g0 & 1U) != 0U)
        return (memF + 1U) & 1U;
    return memF;
}

typedef struct {
    u32 a0, a1, a2;
} stateful_call_args;

void fifo_packet_stateful_call_args(u32 memF_new, u32 memA,
                                    stateful_call_args *o)
{
    o->a0 = STATEFUL_CALL_BASE +
        (memF_new != 0U ? STATEFUL_CALL_ADJ : 0U);
    o->a1 = STATEFUL_CALL_A1;
    o->a2 = memA;
}
