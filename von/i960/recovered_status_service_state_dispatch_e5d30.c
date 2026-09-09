/* Status/service dispatcher recovered from i960 0xe5d30-0xe5d80. */
#include "recovered_common.h"

enum recovered_status_service_state_dispatch_route_e5d30 {
    RECOVERED_STATUS_SERVICE_DISABLED = 0,
    RECOVERED_STATUS_SERVICE_COMMON = 1,
    RECOVERED_STATUS_SERVICE_STATE1 = 2,
    RECOVERED_STATUS_SERVICE_STATE2 = 3
};

typedef struct {
    recovered_u32 route;
    recovered_u32 target;
    recovered_u32 board_byte_admitted;
} recovered_status_service_state_dispatch_result_e5d30;

/*
 * A zero board byte returns before reading the state.  For an admitted byte,
 * state 1 selects the alternate gateway, state 2 selects the profile
 * renderer, and states 0 or >=3 use the common transition gateway.
 */
recovered_status_service_state_dispatch_result_e5d30
recovered_status_service_state_dispatch_e5d30(recovered_u32 board_byte,
                                               recovered_u32 state_5783b4)
{
    recovered_status_service_state_dispatch_result_e5d30 result = {
        RECOVERED_STATUS_SERVICE_DISABLED, 0U, 0U
    };

    if (board_byte == 0U)
        return result;
    result.board_byte_admitted = 1U;
    if (state_5783b4 == 1U) {
        result.route = RECOVERED_STATUS_SERVICE_STATE1;
        result.target = 0x000e61c0U;
    } else if (state_5783b4 == 2U) {
        result.route = RECOVERED_STATUS_SERVICE_STATE2;
        result.target = 0x000e6660U;
    } else {
        result.route = RECOVERED_STATUS_SERVICE_COMMON;
        result.target = 0x000e5da0U;
    }
    return result;
}
