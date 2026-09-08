/* Scheduler gate recovered from i960 0x82ae0-0x82b38. */

#include <stdint.h>

typedef uint32_t u32;

enum recovered_state_scheduler_gate_82ae0_route {
    RECOVERED_SCHEDULER_CONTINUE = 0,
    RECOVERED_SCHEDULER_CALL_82DB0 = 1,
    RECOVERED_SCHEDULER_CALL_81E60 = 2
};

struct recovered_state_scheduler_gate_82ae0 {
    enum recovered_state_scheduler_gate_82ae0_route route;
    u32 ran_timing_selector;
};

struct recovered_state_scheduler_gate_82ae0
recovered_state_scheduler_gate_82ae0(u32 helper_value_503a14,
                                     u32 scheduler_bound,
                                     u32 global_5039f4,
                                     u32 threshold_504dbc,
                                     u32 object_state,
                                     u32 global_504d7c)
{
    struct recovered_state_scheduler_gate_82ae0 plan = {
        RECOVERED_SCHEDULER_CONTINUE, 1U
    };

    /* 0x81f60 runs before any of these branches. */
    if (helper_value_503a14 > scheduler_bound)
        return plan;
    if (global_5039f4 != 4U)
        return plan;
    if (threshold_504dbc >= 6U)
        return plan;
    if (object_state < 8U)
        plan.route = RECOVERED_SCHEDULER_CALL_82DB0;
    else if (global_504d7c == 5U)
        plan.route = RECOVERED_SCHEDULER_CALL_81E60;
    return plan;
}
