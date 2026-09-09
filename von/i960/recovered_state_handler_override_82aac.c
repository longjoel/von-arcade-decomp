/* Optional fall-through override recovered from i960 0x82aac-0x82ae0. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_handler_override_82aac {
    u32 applied;
    u32 action;
    u32 action_504d98;
    u32 marker_504db8;
};

struct recovered_state_handler_override_82aac
recovered_state_handler_override_82aac(u32 object_state, u32 control_504e30)
{
    struct recovered_state_handler_override_82aac out = {0U, 0U, 0U, 0U};

    if (object_state != 3U || (control_504e30 & 4U) == 0U ||
        (control_504e30 & 24U) != 0U)
        return out;
    out.applied = 1U;
    out.action = 6U;
    out.action_504d98 = 6U;
    out.marker_504db8 = 20U;
    return out;
}
