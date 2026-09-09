/* Publication mapper recovered from i960 0x86c08-0x86cb4. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_stage_publication_entry_86c08 {
    RECOVERED_STAGE_PUBLICATION_FROM_86C08 = 0,
    RECOVERED_STAGE_PUBLICATION_FROM_86C64 = 1
};

struct recovered_stage_publication_map_86c08 {
    u32 entry;
    int32_t value_503aa4;
    u32 publication_51c9a4;
    u32 publication_51c9ac;
    u32 publication_address_1;
    u32 publication_address_2;
    u32 continuation;
};

struct recovered_stage_publication_map_86c08
recovered_stage_publication_map_86c08(u32 entry, int32_t value_503aa4)
{
    struct recovered_stage_publication_map_86c08 out;

    out.entry = entry;
    out.value_503aa4 = value_503aa4;
    out.publication_address_1 = 0x0051c9a4U;
    out.publication_address_2 = 0x0051c9acU;

    if (entry == RECOVERED_STAGE_PUBLICATION_FROM_86C64) {
        out.publication_51c9a4 = 12U;
        out.publication_51c9ac = (value_503aa4 == 0 || value_503aa4 == 1)
                                     ? 1U : 0xb4U;
    } else if (value_503aa4 == 0) {
        out.publication_51c9a4 = 12U;
        out.publication_51c9ac = 1U;
    } else if (value_503aa4 == 1) {
        out.publication_51c9a4 = 19U;
        out.publication_51c9ac = 0xb4U;
    } else if (value_503aa4 == 2) {
        out.publication_51c9a4 = 12U;
        out.publication_51c9ac = 0xb4U;
    } else {
        out.publication_51c9a4 = 19U;
        out.publication_51c9ac = 0xb4U;
    }
    out.continuation = 0x00086cb8U;
    return out;
}
