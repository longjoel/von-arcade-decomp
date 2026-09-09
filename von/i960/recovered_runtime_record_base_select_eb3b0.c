/* Runtime record-base selector recovered from i960 0xeb3b0-eb448. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 primary_match[4];
    recovered_u32 alternate_match[4];
    recovered_u32 primary_all_one;
    recovered_u32 alternate_all_one;
    recovered_u32 selected_base;
    recovered_u32 selected_family;
    recovered_u32 publication_address;
    recovered_u32 continuation_target;
    recovered_u32 primary_base;
    recovered_u32 alternate_base;
    recovered_u32 fallback_base;
} recovered_runtime_record_base_select_result_eb3b0;

recovered_runtime_record_base_select_result_eb3b0
recovered_runtime_record_base_select_eb3b0(const recovered_u32 primary_match[4],
                                           const recovered_u32 alternate_match[4],
                                           recovered_u32 continuation_target)
{
    recovered_runtime_record_base_select_result_eb3b0 result;
    recovered_u32 i;

    for (i = 0U; i < 4U; ++i) {
        result.primary_match[i] = primary_match[i];
        result.alternate_match[i] = alternate_match[i];
    }
    result.primary_all_one = 1U;
    result.alternate_all_one = 1U;
    for (i = 0U; i < 4U; ++i) {
        if (primary_match[i] != 1U)
            result.primary_all_one = 0U;
        if (alternate_match[i] != 1U)
            result.alternate_all_one = 0U;
    }
    result.primary_base = 0x00200000U;
    result.alternate_base = 0x01080000U;
    result.fallback_base = 0x005e0000U;
    if (result.primary_all_one) {
        result.selected_base = result.primary_base;
        result.selected_family = 0U;
    } else if (result.alternate_all_one) {
        result.selected_base = result.alternate_base;
        result.selected_family = 1U;
    } else {
        result.selected_base = result.fallback_base;
        result.selected_family = 2U;
    }
    result.publication_address = 0x00501cc4U;
    result.continuation_target = continuation_target;
    return result;
}
