/* Selector routing bridge recovered from i960 0x8c0c8-0x8c0e0. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 selector;
    recovered_u32 entry_gate_equal;
    recovered_u32 selector_above_one;
    recovered_u32 selector_zero;
    recovered_u32 selector_two;
    recovered_u32 continuation;
} recovered_startup_mode4_common_dispatch_8c0c8_selector_routes_result;

recovered_startup_mode4_common_dispatch_8c0c8_selector_routes_result
recovered_startup_mode4_common_dispatch_8c0c8_selector_routes(
    recovered_u32 selector, recovered_u32 entry_gate_equal)
{
    recovered_startup_mode4_common_dispatch_8c0c8_selector_routes_result result;

    result.selector = selector;
    result.entry_gate_equal = entry_gate_equal != 0U ? 1U : 0U;
    result.selector_above_one = selector > 1U ? 1U : 0U;
    result.selector_zero = selector == 0U ? 1U : 0U;
    result.selector_two = selector == 2U ? 1U : 0U;
    if (result.entry_gate_equal != 0U)
        result.continuation = 0x0008c2ccU;
    else if (selector == 0U)
        result.continuation = 0x0008c0e0U;
    else if (selector == 2U)
        result.continuation = 0x0008c660U;
    else
        result.continuation = 0x0008c760U;
    return result;
}
