/* Secondary stage service bridge recovered from i960 0x87bbc-0x87c2c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_stage_secondary_service_bridge_87bbc {
    u32 first_buffer;
    u32 second_buffer;
    u32 callback_503ad4;
    u32 callback_5040d4;
    u32 call_targets[9];
    u32 call_buffer_arguments[9];
};

struct recovered_stage_secondary_service_bridge_87bbc
recovered_stage_secondary_service_bridge_87bbc(u32 callback_503ad4,
                                               u32 callback_5040d4)
{
    struct recovered_stage_secondary_service_bridge_87bbc out;

    out.first_buffer = 0x00503ad0U;
    out.second_buffer = 0x005040d0U;
    out.callback_503ad4 = callback_503ad4;
    out.callback_5040d4 = callback_5040d4;
    out.call_targets[0] = 0x000de990U;
    out.call_targets[1] = 0x000be1f0U;
    out.call_targets[2] = 0x000bd730U;
    out.call_targets[3] = callback_503ad4;
    out.call_targets[4] = 0x00023980U;
    out.call_targets[5] = 0x000df070U;
    out.call_targets[6] = 0x00026cb8U;
    out.call_targets[7] = 0x000bd810U;
    out.call_targets[8] = callback_5040d4;
    out.call_buffer_arguments[0] = 0U;
    out.call_buffer_arguments[1] = out.first_buffer;
    out.call_buffer_arguments[2] = out.first_buffer;
    out.call_buffer_arguments[3] = out.first_buffer;
    out.call_buffer_arguments[4] = out.first_buffer;
    out.call_buffer_arguments[5] = out.first_buffer;
    out.call_buffer_arguments[6] = out.second_buffer;
    out.call_buffer_arguments[7] = out.second_buffer;
    out.call_buffer_arguments[8] = out.second_buffer;
    return out;
}
