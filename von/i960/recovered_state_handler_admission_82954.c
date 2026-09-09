/* Common handler admission gate recovered from i960 0x82954-0x82a10. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_state_handler_admission_82954 {
    u32 route;
    u32 target;
    u32 status;
};

enum {
    RECOVERED_HANDLER_ROUTE_OVERRIDE = 0U,
    RECOVERED_HANDLER_ROUTE_COMMIT = 1U
};

struct recovered_state_handler_admission_82954
recovered_state_handler_admission_82954(u32 status, u32 control_504e30,
                                        u32 control_504dc8,
                                        u32 object_state,
                                        int32_t global_504d60,
                                        int32_t timing_value,
                                        int32_t timing_threshold)
{
    struct recovered_state_handler_admission_82954 out = {
        RECOVERED_HANDLER_ROUTE_OVERRIDE, 0x00082aacU, status
    };
    u32 required_bit = 0U;

    if (status == 29U)
        required_bit = 3U;
    else if (status == 30U)
        required_bit = 4U;
    else if (status == 31U)
        required_bit = 5U;
    if (required_bit != 0U && control_504dc8 == 1U &&
        (control_504e30 & (1U << required_bit)) != 0U) {
        out.route = RECOVERED_HANDLER_ROUTE_COMMIT;
        out.target = 0x00082a10U;
        return out;
    }

    if (status >= 13U && status <= 15U && control_504dc8 == 1U &&
        global_504d60 < 0 && object_state == 6U &&
        timing_value < timing_threshold) {
        out.route = RECOVERED_HANDLER_ROUTE_COMMIT;
        out.target = 0x00082a10U;
    }
    return out;
}
