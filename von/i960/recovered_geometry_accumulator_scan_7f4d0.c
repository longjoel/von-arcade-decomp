/* Pure byte-table candidate scan from i960 0x7f4d0-0x7f6b0. */
#include "recovered_common.h"
recovered_u32 recovered_geometry_accumulator_scan_7f4d0(
    const recovered_u32 *table, const recovered_u32 *peer,
    const recovered_u32 *metric, recovered_u32 *selected_metric)
{
    recovered_u32 selected = 0xffffffffU, index;
    for (index=0; index<32U; ++index) {
        recovered_u32 a=table[index]&0xffU, b=peer[index]&0xffU;
        if (a && b>=a && b<a+5U && metric[index]<*selected_metric) {
            *selected_metric=metric[index]; selected=index;
        }
    }
    return selected;
}
