/* Shared state-2 status tail recovered from i960 0xe6c50-0xe6d3c. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 remainder;
    recovered_u32 route;
    recovered_u32 status_504d2c;
    recovered_u32 status_504d2e;
    recovered_u32 status_504d24;
    recovered_u32 status_504d26;
    recovered_u32 table_address;
    recovered_u32 table_halfword_count;
    recovered_u32 return_helper_target;
    recovered_u32 return_helper_remainder;
    recovered_u32 continuation;
} recovered_status_service_state2_common_tail_result_e6c50;

enum recovered_status_service_state2_common_tail_route_e6c50 {
    RECOVERED_STATUS_STATE2_TAIL_CLEAR = 0,
    RECOVERED_STATUS_STATE2_TAIL_PROGRAM = 1
};

recovered_status_service_state2_common_tail_result_e6c50
recovered_status_service_state2_common_tail_e6c50(recovered_u32 remainder)
{
    recovered_status_service_state2_common_tail_result_e6c50 result;
    int32_t signed_remainder = (int32_t)remainder;
    int32_t delta_438 = signed_remainder - 0x438;
    int32_t delta_654;

    result.remainder = remainder;
    result.route = RECOVERED_STATUS_STATE2_TAIL_CLEAR;
    result.status_504d2c = 0;
    result.status_504d2e = 0;
    result.status_504d24 = 0;
    result.status_504d26 = 0;
    result.table_address = 0;
    result.table_halfword_count = 0;
    result.return_helper_target = 0x0001c618U;
    result.return_helper_remainder = 0x86fU;
    result.continuation = 0x000e6d3cU;

    if (delta_438 >= 0 && delta_438 <= 0x40) {
        delta_654 = delta_438;
    } else if (delta_438 > 0x40) {
        delta_654 = signed_remainder - 0x654;
        if (delta_654 > 0x40 || delta_654 < 0)
            return result;
    } else {
        return result;
    }

    result.route = RECOVERED_STATUS_STATE2_TAIL_PROGRAM;
    result.status_504d2c = 0x4000U;
    result.status_504d24 = 0x8000U;
    result.status_504d26 = 0;
    result.table_address = 0x00577fb0U;
    result.table_halfword_count = 0x200U;
    return result;
}

recovered_u32 recovered_status_service_state2_table_value_e6c50(
    recovered_u32 remainder, recovered_u32 table_index)
{
    int32_t signed_remainder = (int32_t)remainder;
    int32_t delta = signed_remainder - 0x438;
    int32_t value;

    if (delta < 0 || delta > 0x40) {
        delta = signed_remainder - 0x654;
        if (delta < 0 || delta > 0x40)
            return 0;
    }
    if (table_index < 0x63U || table_index > 0x123U)
        return 0;

    value = 0x200 - (delta << 3);
    if (value < 0)
        value = -value;
    return (recovered_u32)value;
}
