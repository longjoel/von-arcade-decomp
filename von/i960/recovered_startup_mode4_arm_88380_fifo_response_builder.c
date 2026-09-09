/* Slot-20 response FIFO builder recovered from i960 0x88380-0x88440. */
#include "recovered_common.h"

typedef struct {
    recovered_u32 setup_call, setup_argument, setup_seed;
    recovered_u32 endpoint_a0, endpoint_a1, endpoint_b0, endpoint_b1;
    recovered_u32 delta_a, delta_b;
    recovered_u32 packet10[3], packet31[7];
    recovered_u32 fifo_address;
} recovered_startup_mode4_arm_result_88380_fifo_response_builder;

int recovered_startup_mode4_arm_88380_fifo_response_builder(
    recovered_u32 endpoint_a0, recovered_u32 endpoint_a1,
    recovered_u32 endpoint_b0, recovered_u32 endpoint_b1,
    recovered_startup_mode4_arm_result_88380_fifo_response_builder *result)
{
    recovered_startup_mode4_arm_result_88380_fifo_response_builder r = {0};
    r.setup_call = 0x2a990U;
    r.setup_argument = 0xd000U;
    r.setup_seed = 0U;
    r.endpoint_a0 = endpoint_a0;
    r.endpoint_a1 = endpoint_a1;
    r.endpoint_b0 = endpoint_b0;
    r.endpoint_b1 = endpoint_b1;
    r.delta_a = endpoint_b0 - endpoint_a0;
    r.delta_b = endpoint_b1 - endpoint_a1;
    r.packet10[0] = 10U;
    r.packet10[1] = r.delta_b;
    r.packet10[2] = r.delta_a;
    r.packet31[0] = 31U;
    r.packet31[1] = endpoint_a0;
    r.packet31[2] = endpoint_b0;
    r.packet31[3] = 0U;
    r.packet31[4] = 0U;
    r.packet31[5] = endpoint_a1;
    r.packet31[6] = endpoint_b1;
    r.fifo_address = 0x884000U;
    return result != (void *)0 ? (*result = r, 1) : 1;
}
