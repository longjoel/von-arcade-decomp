/* Exact host-side write contract recovered from i960 routine 0x6fec0. */
#include <stdint.h>

typedef uint32_t u32;

typedef void (*recovered_geometry_control_write)(void *opaque,
                                                  u32 address,
                                                  u32 value);

/*
 * Selector zero emits one 64-bit store followed by four word stores.  The
 * second word of the paired store is retained here even though the original
 * disassembly loads it into a register that is not otherwise referenced.
 */
u32 recovered_geometry_control_selector_6fec0(
    u32 selector,
    recovered_geometry_control_write write,
    void *opaque)
{
    if (selector != 0U)
        return 0U;

    write(opaque, 0x00800030U, 0x00000303U);
    write(opaque, 0x00804000U, 0x00000080U);
    write(opaque, 0x00804004U, 0x01f40204U);
    write(opaque, 0x00804008U, 0x00f80140U);
    write(opaque, 0x0080400cU, 0x00f80140U);
    write(opaque, 0x00804000U, 0x00f80140U);
    write(opaque, 0x00804000U, 0x00f80140U);
    return 1U;
}
