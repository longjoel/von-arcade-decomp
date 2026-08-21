typedef unsigned long u32;

/* Model 2B host work RAM.  The smoke test makes execution observable without
 * depending on the original game's I/O or coprocessor initialization. */
#define WORKRAM ((volatile u32 *)0x00500000)

void i960_prototype_main(void)
{
    volatile u32 *const marker = WORKRAM;

    *marker = 0x49393630UL;
    marker[1] = 0x50524F54UL;
    marker[2] = marker[2] + 1;

    for (;;)
        marker[3] = marker[3] + 1;
}
