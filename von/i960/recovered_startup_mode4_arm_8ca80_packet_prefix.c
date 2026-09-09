/* Shared response packet prefix recovered from i960 0x8cac8/0x8ccfc. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 entry;
    recovered_u32 endpoint_a0, endpoint_a1, endpoint_b0, endpoint_b1;
    recovered_u32 delta_a, delta_b;
    recovered_u32 fifo_response, masked_lane;
    recovered_u32 packet10[3], packet29[3], packet30[3];
    recovered_u32 fifo_address, command29_constant, command30_constant;
    recovered_u32 continuation;
} recovered_startup_mode4_arm_result_8ca80_packet_prefix;

int recovered_startup_mode4_arm_8ca80_packet_prefix(
    recovered_u32 entry, recovered_u32 endpoint_a0, recovered_u32 endpoint_a1,
    recovered_u32 endpoint_b0, recovered_u32 endpoint_b1,
    recovered_u32 fifo_response,
    recovered_startup_mode4_arm_result_8ca80_packet_prefix *result)
{
    recovered_startup_mode4_arm_result_8ca80_packet_prefix r = {0};
    r.entry = entry;
    r.endpoint_a0 = endpoint_a0;
    r.endpoint_a1 = endpoint_a1;
    r.endpoint_b0 = endpoint_b0;
    r.endpoint_b1 = endpoint_b1;
    r.delta_a = endpoint_b0 - endpoint_a0;
    r.delta_b = endpoint_b1 - endpoint_a1;
    r.fifo_response = fifo_response;
    r.masked_lane = (fifo_response + 0x3000U) & 0xffffU;
    r.packet10[0] = 10U;
    r.packet10[1] = r.delta_b;
    r.packet10[2] = r.delta_a;
    r.packet29[0] = 29U;
    r.packet29[1] = r.masked_lane;
    r.packet29[2] = 0x42200000U;
    r.packet30[0] = 30U;
    r.packet30[1] = r.masked_lane;
    r.packet30[2] = 0x42200000U;
    r.fifo_address = 0x884000U;
    r.command29_constant = 0x42200000U;
    r.command30_constant = 0x42200000U;
    r.continuation = entry == 0x8cac8U ? 0x8cb00U : 0x8cd30U;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
