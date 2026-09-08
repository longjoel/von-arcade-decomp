/* Geometry FIFO command packet, i960 routine 0x00092830-0x000928d4.
 *
 * Byte-identical template to 0x934b0 (same 12-word packet to the
 * 0x884000 host FIFO, same tail call to 0x8e310); only the site
 * constants differ: tail-call base 0x02b4a4bc, offset 0x98750, and the
 * call-arg word reloaded from [0x562494]. Shares the packet core via
 * the 0x934b0 translation unit.
 *
 * Decoded from von/build/disasm/vonj-maincpu.lst.
 */

#include "von/i960/recovered_geometry_fifo_packet_934b0.c"

#define SITE92830_BASE 0x02b4a4bcU
#define SITE92830_OFF 0x98750U

void fifo_packet_92830_tail_args(u32 mem562494, tail_call_args *o)
{
    fifo_packet_tail_args_p(SITE92830_BASE, SITE92830_OFF, mem562494, o);
}
