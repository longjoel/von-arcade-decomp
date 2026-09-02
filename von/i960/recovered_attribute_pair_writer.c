/* Direct attribute-pair writer recovered from i960 0x20300. */

#include <stdint.h>

typedef uint32_t u32;

struct recovered_attribute_pair_plan {
    u32 return_stub;
    u32 source_first;
    u32 source_second;
    u32 destination_first;
    u32 destination_second;
    u32 byte_offset;
    u32 attribute_bits;
};

void recovered_attribute_pair_plan(u32 selector, u32 index,
                                   struct recovered_attribute_pair_plan *plan)
{
    plan->return_stub = 0x0002038cU;
    plan->source_first = selector == 0U ? 0x02fe3214U : 0x02fe3218U;
    plan->source_second = selector == 0U ? 0x02fe3216U : 0x02fe321aU;
    plan->destination_first = selector == 0U ? 0x01001288U : 0x01001290U;
    plan->destination_second = selector == 0U ? 0x0100128aU : 0x01001292U;
    plan->byte_offset = index * 14U;
    plan->attribute_bits = 0xc000U;
}
