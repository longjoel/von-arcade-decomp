/* Object-branch dispatcher recovered from i960 0x237ac-0x2381c. */
#include <stdint.h>
#include "recovered_common.h"

typedef uint32_t u32;

enum recovered_geometry_object_branch {
    RECOVERED_GEOMETRY_TRANSFORM_FIRST = 0,
    RECOVERED_GEOMETRY_TRANSFORM_SECOND = 1,
    RECOVERED_GEOMETRY_ALTERNATE = 2,
};

struct recovered_geometry_object_branch_plan {
    u32 route;
    u32 object_flag_18;
    u32 first_window;
    int32_t first_response;
    u32 first_window_pass;
    u32 first_response_pass;
    u32 second_window;
    int32_t second_response;
    u32 second_window_pass;
    u32 second_response_pass;
};

void recovered_geometry_object_branch_dispatch_plan(
    u32 object_flag_18, u32 delta_g6, u32 response_g7,
    struct recovered_geometry_object_branch_plan *plan)
{
    plan->object_flag_18 = object_flag_18 & 0xffU;
    plan->first_window = (delta_g6 + 0x17ffU) & 0xffffU;
    plan->first_response = recovered_sign_extend_16(response_g7);
    plan->first_window_pass = plan->first_window <= 0x2ffeU ? 1U : 0U;
    plan->first_response_pass = plan->first_response >= -0xdff ? 1U : 0U;
    plan->second_window = (delta_g6 + 0x1ffU) & 0xffffU;
    plan->second_response = recovered_sign_extend_16(response_g7);
    plan->second_window_pass = plan->second_window <= 0x3feU ? 1U : 0U;
    plan->second_response_pass = plan->second_response >= -0xbff ? 1U : 0U;

    if (plan->object_flag_18 == 0U && plan->first_window_pass &&
        plan->first_response_pass) {
        plan->route = RECOVERED_GEOMETRY_TRANSFORM_FIRST;
    } else if (plan->object_flag_18 == 0U &&
               plan->second_window_pass && plan->second_response_pass) {
        plan->route = RECOVERED_GEOMETRY_TRANSFORM_SECOND;
    } else {
        plan->route = RECOVERED_GEOMETRY_ALTERNATE;
    }
}
