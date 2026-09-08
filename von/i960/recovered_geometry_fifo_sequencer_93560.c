/* Geometry FIFO sequencer, i960 routine 0x00093560-0x000936f0.
 *
 * Decoded from von/build/disasm/vonj-maincpu.lst. Emits the fixed
 * 12-word prefix packet to the host FIFO at 0x884000
 * ([5, 18, g0, g1, g2, 21, g3 & 0xffff, 19, 0x3e4ccccd x3, 6];
 * the closing 6 is stored after the single tail call), then makes
 * exactly one tail call to the already-recovered 0x8e310 packet
 * tail, which is outside this contract.
 *
 * Between packet and call, two RAM cells drive a selector/sequencer:
 * C8 = [0x5624c8], CC = [0x5624cc].
 * - If CC == 0, the 0xf5058 subroutine runs (outside this contract;
 *   its g0 result arrives as an input) and C8 = g0 & 3 is stored.
 * - C8 == 1 selects base 0x02b5c3a6, C8 == 2 selects 0x02b60728;
 *   either jumps to the modulo-120 path: CC = (CC + 1) % 120 and the
 *   call is {base, 0x02be2b64, CC}.
 * - Otherwise the modulo-168 sequencer runs with base 0x02b58024:
 *   CC = (CC + 1) % 168; g1 is always base + 0x8ab40 (0x02be2b64);
 *   the g2 call word is CC when CC <= 59, else with t = CC - 60:
 *   60 when t < 23, else with u = CC - 84: 0x77 when u > 59
 *   (unsigned), else CC - 24.
 * Comparisons mirror the listing: signed greater for the 59 way,
 * unsigned less/greater for the 23/59 ways.
 */

typedef unsigned int u32;

#define SEQ_FILL_CONST 0x3e4ccccdU
#define SEQ_PACKET_WORDS 12U
#define SEQ_BASE_C1 0x02b5c3a6U
#define SEQ_BASE_C2 0x02b60728U
#define SEQ_BASE_SEQ 0x02b58024U
#define SEQ_A1_CONST 0x02be2b64U
#define SEQ_A1_OFF 0x8ab40U

void fifo_seq_packet_build(u32 g0, u32 g1, u32 g2, u32 g3, u32 *words)
{
    words[0] = 5U;
    words[1] = 18U;
    words[2] = g0;
    words[3] = g1;
    words[4] = g2;
    words[5] = 21U;
    words[6] = g3 & 0xffffU;
    words[7] = 19U;
    words[8] = SEQ_FILL_CONST;
    words[9] = SEQ_FILL_CONST;
    words[10] = SEQ_FILL_CONST;
    words[11] = 6U;
}

typedef struct {
    u32 wrote_c8;
    u32 c8_new;
    u32 cc_new;
    u32 a0, a1, a2;
} seq_step_out;

void fifo_seq_step(u32 post_bal_g0, u32 memC8, u32 memCC,
                   seq_step_out *o)
{
    u32 c8 = memC8;
    o->wrote_c8 = 0U;
    if (memCC == 0U) {
        c8 = post_bal_g0 & 3U;
        o->wrote_c8 = 1U;
    }
    o->c8_new = c8;
    if (c8 == 1U || c8 == 2U) {
        u32 n2 = (memCC + 1U) % 120U;
        o->cc_new = n2;
        o->a0 = (c8 == 1U) ? SEQ_BASE_C1 : SEQ_BASE_C2;
        o->a1 = SEQ_A1_CONST;
        o->a2 = n2;
        return;
    }
    {
        u32 n2 = (memCC + 1U) % 168U;
        u32 g2;
        o->cc_new = n2;
        o->a0 = SEQ_BASE_SEQ;
        o->a1 = SEQ_BASE_SEQ + SEQ_A1_OFF;
        if ((int)n2 > 59) {
            u32 t = n2 - 60U;
            if (t < 23U) {
                g2 = 60U;
            } else {
                u32 u = n2 - 84U;
                g2 = (u > 59U) ? 0x77U : n2 - 24U;
            }
        } else {
            g2 = n2;
        }
        o->a2 = g2;
    }
}
