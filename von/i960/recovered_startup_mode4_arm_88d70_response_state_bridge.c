/* Response-to-state bridge recovered from i960 0x88d70-0x88da8. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_startup_mode4_arm_88d70_response_state_bridge {
    u32 record_184;
    u32 first_fifo_response;
    u32 record_8;
    u32 second_fifo_response;
    u32 record_10;
    u32 derived_51c950;
    u32 derived_51c954;
    u32 state_51c940;
    u32 state_51c948;
    u32 address_51c940;
    u32 address_51c948;
    u32 continuation;
};

struct recovered_startup_mode4_arm_88d70_response_state_bridge
recovered_startup_mode4_arm_88d70_response_state_bridge(
    u32 record_184, u32 first_fifo_response, u32 record_8,
    u32 second_fifo_response, u32 record_10)
{
    struct recovered_startup_mode4_arm_88d70_response_state_bridge out;

    out.record_184 = record_184;
    out.first_fifo_response = first_fifo_response;
    out.record_8 = record_8;
    out.second_fifo_response = second_fifo_response;
    out.record_10 = record_10;
    out.derived_51c950 = first_fifo_response + record_8;
    out.derived_51c954 = record_10 - second_fifo_response;
    out.state_51c940 = record_184;
    out.state_51c948 = 0x42a00000U;
    out.address_51c940 = 0x0051c940U;
    out.address_51c948 = 0x0051c948U;
    out.continuation = 0x00088da8U;
    return out;
}
