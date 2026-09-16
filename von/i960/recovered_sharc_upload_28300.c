/* Runnable SHARC program upload and boot, recovered from i960 0x28300-0x28408.
 *
 * Reproduces the host sequence: latch the 0x2b1e word count, raise the copro
 * upload control bit (0x980000 bit 31), clear the bank register (0x980020),
 * configure the SHARC external-port IOP registers at 0x8c0000, stream the
 * 0x2b1e 16-bit bootstrap words embedded at 0x16b58c into the copro FIFO
 * (0x884000, external-DMA 16/48 packing), clear the control bit to boot, then
 * emit the 8 sync word that starts the SHARC service loop.
 */

typedef unsigned int u32;
typedef unsigned short u16;

#define RECOVERED_SHARC_UPLOAD_WORDS 0x2b1eU
#define RECOVERED_SHARC_UPLOAD_SOURCE 0x0016b58cU

void recovered_sharc_upload_run(void)
{
    volatile u32 *const ctl = (volatile u32 *)0x00980000U;
    volatile u32 *const bank = (volatile u32 *)0x00980020U;
    volatile u32 *const iop = (volatile u32 *)0x008c0000U;
    volatile u32 *const fifo = (volatile u32 *)0x00884000U;
    volatile const u16 *const source = (volatile const u16 *)RECOVERED_SHARC_UPLOAD_SOURCE;
    u32 index;

    *(volatile u32 *)0x00503ac4U = RECOVERED_SHARC_UPLOAD_WORDS;

    *ctl = 0x80000000U;
    *bank = 0U;

    iop[0] = 0xa100U;
    iop[0] = 0U;
    iop[2] = 0xc9400U;      /* +0x08 */
    iop[0x1c] = 0U;         /* +0x70 */
    iop[0x40] = 0x20000U;   /* +0x100 */
    iop[0x41] = 1U;         /* +0x104 */
    iop[0x42] = 0xe5fU;     /* +0x108 */
    iop[0] = 0xa110U;
    iop[0x1c] = 0xa1U;      /* +0x70 */
    iop[0x1c] = 0U;

    for (index = 0U; index < RECOVERED_SHARC_UPLOAD_WORDS; ++index)
        *fifo = (u32)source[index];

    *ctl = 0U;
    *fifo = 8U;
}
