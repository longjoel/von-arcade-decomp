/* Status-to-action commit recovered from i960 0x82a10-0x82aac. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_handler_commit_82a10 {
    u32 entered;
    u32 action;
    u32 stores;
    u32 marker_504db4;
    u32 marker_504db8;
    u32 action_504d98;
};

struct recovered_state_handler_commit_82a10
recovered_state_handler_commit_82a10(u32 entered, u32 status,
                                     u32 unused_object_state,
                                     u32 unused_control_504e30)
{
    struct recovered_state_handler_commit_82a10 out = {
        entered != 0U, 0U, 0U, 0U, 0U, 0U
    };

    if (entered == 0U)
        return out;
    (void)unused_object_state;
    (void)unused_control_504e30;
    out.action = status == 29U ? 17U : status == 30U ? 18U :
                 status == 31U ? 16U :
                 (status == 13U || status == 14U || status == 15U) ? 6U : 16U;
    out.stores = 1U;
    out.marker_504db4 = UINT32_MAX;
    out.marker_504db8 = 20U;
    out.action_504d98 = out.action;
    return out;
}
