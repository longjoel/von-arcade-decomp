/* Shared object/context routing recovered from i960 0xbf180-0xbf238. */
#include "recovered_common.h"

typedef enum {
    RECOVERED_OBJECT_ROUTE_A1050 = 0,
    RECOVERED_OBJECT_ROUTE_A98F0 = 1,
    RECOVERED_OBJECT_ROUTE_A55E0 = 2
} recovered_object_route_family_bf180;

typedef struct {
    recovered_u32 callee;
    recovered_u32 object_subtable;
    recovered_u32 context_base;
    recovered_u32 special_object;
} recovered_object_dispatch_context_plan_bf180;

int recovered_object_dispatch_context_bf180(
    recovered_object_route_family_bf180 family,
    recovered_u32 object_pointer,
    recovered_object_dispatch_context_plan_bf180 *plan)
{
    static const recovered_u32 callees[3] = {
        0x000a1050U, 0x000a98f0U, 0x000a55e0U
    };

    if ((unsigned)family >= 3U || plan == (void *)0)
        return 0;
    plan->callee = callees[family];
    plan->object_subtable = object_pointer + 0x200U;
    plan->special_object = object_pointer == 0x00503ad0U ? 1U : 0U;
    plan->context_base = plan->special_object ? 0x00565320U : 0x005658a0U;
    return 1;
}
