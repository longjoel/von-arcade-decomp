/* Geometry FIFO command packet, i960 routine 0x000934b0-0x00093550.
 *
 * Decoded from von/build/disasm/vonj-maincpu.lst. Emits a fixed 12-word
 * command packet to the host FIFO at 0x884000 (host 0x00884000 -> FIFO
 * -> SHARC data read; see disassembly-annotations.md), then tail-calls
 * the already-recovered 0x8e310 packet tail, which is outside this
 * contract:
 *   w0 = 5, w1 = 18, w2 = g0, w3 = g1, w4 = g2, w5 = 21,
 *   w6 = g3 & 0xffff (shlo 16 / shri 16),
 *   w7 = 19, w8 = w9 = w10 = 0x3e4ccccd (0.2f), w11 = 6.
 * The incoming g0/g1/g2 are stored first, then g0/g1 are reused to form
 * the tail-call args (g0 = 0x02b68d3a, g1 = g0 + 0x79e2a) while g2 is
 * reloaded from [0x562490] for the call. The reload has no effect on
 * the packet, which keeps the incoming g2.
 *
 * Observed caller goldens (packet words w2/w3/w4/w6):
 * 0x99afc: g0 = 0, g1 = 0x4181999a, g2 = 0xc0666666, g3 = 0xffffc000.
 * 0x96988: g0 = 0x40800000, g1 = 0x4240cccd, g2 = 0x416ccccd,
 *          g3 = 0xffffc000.
 */

typedef unsigned int u32;

#define FIFO_PACKET_WORDS 12U
#define FIFO_CMD_W8_CONST 0x3e4ccccdU
#define TAIL_CALL_A0 0x02b68d3aU
#define TAIL_CALL_A1_OFF 0x79e2aU

void fifo_packet_build(u32 g0, u32 g1, u32 g2, u32 g3, u32 *words)
{
    words[0] = 5U;
    words[1] = 18U;
    words[2] = g0;
    words[3] = g1;
    words[4] = g2;
    words[5] = 21U;
    words[6] = g3 & 0xffffU;
    words[7] = 19U;
    words[8] = FIFO_CMD_W8_CONST;
    words[9] = FIFO_CMD_W8_CONST;
    words[10] = FIFO_CMD_W8_CONST;
    words[11] = 6U;
}

typedef struct {
    u32 a0, a1, a2;
} tail_call_args;

void fifo_packet_tail_args(u32 mem562490, tail_call_args *o)
{
    o->a0 = TAIL_CALL_A0;
    o->a1 = TAIL_CALL_A0 + TAIL_CALL_A1_OFF;
    o->a2 = mem562490;
}
