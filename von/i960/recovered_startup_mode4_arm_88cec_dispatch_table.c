/* Six-arm dispatch table recovered from i960 0x88cec-0x88d00. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_startup_mode4_arm_88cec_dispatch_table {
    u32 selector;
    u32 table_address;
    u32 entry_address;
    u32 target_address;
    u32 entry_count;
    u32 in_range;
};

struct recovered_startup_mode4_arm_88cec_dispatch_table
recovered_startup_mode4_arm_88cec_dispatch_table(u32 selector)
{
    static const u32 targets[6] = {
        0x00088d04U, 0x00088ea0U, 0x0008903cU,
        0x0008931cU, 0x00089930U, 0x00089814U
    };
    struct recovered_startup_mode4_arm_88cec_dispatch_table out;

    out.selector = selector;
    out.table_address = 0x00088cecu;
    out.entry_count = 6U;
    out.in_range = selector < out.entry_count ? 1U : 0U;
    out.entry_address = out.table_address + (selector * 4U);
    out.target_address = out.in_range != 0U ? targets[selector] : 0U;
    return out;
}
