/* Status profile selector dispatch recovered from i960 0xe6500-0xe6578. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 input_selector;
    recovered_u32 bounded_selector;
    recovered_u32 selected_profile;
    recovered_u32 dispatch_table;
    recovered_u32 loop_target;
    recovered_u32 return_target;
} recovered_status_profile_selector_dispatch_result_e6500;

recovered_status_profile_selector_dispatch_result_e6500
recovered_status_profile_selector_dispatch_e6500(recovered_u32 selector)
{
    static const recovered_u32 profile_map[8] = {0, 4, 3, 7, 1, 2, 6, 5};
    recovered_status_profile_selector_dispatch_result_e6500 result;

    result.input_selector = selector;
    result.bounded_selector = selector <= 7U ? selector : 0U;
    result.selected_profile = profile_map[result.bounded_selector];
    result.dispatch_table = 0x000e651cU;
    result.loop_target = 0x000e6578U;
    result.return_target = 0x000e6640U;
    return result;
}
