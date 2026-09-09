/* Secondary response-buffer/setup block recovered from i960 0x87e70-0x87ee0. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_secondary_response_buffer_setup_87e70 {
    int32_t state_value;
    u32 upload_admitted;
    u32 first_source;
    u32 second_source;
    u32 first_destination;
    u32 second_destination;
    u32 upload_bytes;
    u32 upload_call;
    u32 callback_first_address;
    u32 callback_second_address;
    u32 callback_value;
    u32 callback_store_count;
    u32 phase_address;
    u32 phase_value;
    u32 formatter_target;
    u32 formatter_argument_0;
    u32 formatter_argument_1;
    u32 renderer_source;
    u32 renderer_target;
};

struct recovered_stage_secondary_response_buffer_setup_87e70
recovered_stage_secondary_response_buffer_setup_87e70(int32_t state_value,
                                                      u32 seed_value)
{
    struct recovered_stage_secondary_response_buffer_setup_87e70 out;

    out.state_value = state_value;
    out.upload_admitted = state_value < 0 ? 1U : 0U;
    out.first_source = 0x0051c9e0U;
    out.second_source = 0x0051cfe0U;
    out.first_destination = 0x00503ad0U;
    out.second_destination = 0x005040d0U;
    out.upload_bytes = 0x600U;
    out.upload_call = 0x000f5d40U;
    out.callback_first_address = 0x00503c4aU;
    out.callback_second_address = 0x0050424aU;
    out.callback_value = seed_value;
    out.callback_store_count = 2U;
    out.phase_address = 0x00503a00U;
    out.phase_value = 12U;
    out.formatter_target = 0x0001cac8U;
    out.formatter_argument_0 = 21U;
    out.formatter_argument_1 = 14U;
    out.renderer_source = 0x00087aa0U;
    out.renderer_target = 0x0001da90U;
    return out;
}
