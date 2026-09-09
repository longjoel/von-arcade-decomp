/* Startup status classifier/service gate recovered from i960 0x18a10-0x18aac. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_startup_status_helper_18a10 {
    u32 mode_byte;
    u32 state_flag;
    u32 status_service_result;
    u32 service_gate_open;
    u32 state_service_calls;
    u32 status_address;
    u32 state_address;
    u32 flag_address;
    u32 status_service_call;
    u32 state_service_call;
    u32 loop_first_index;
    u32 loop_last_index;
};

void recovered_startup_status_helper_18a10(
    u32 hardware_status, u32 status_service_result, u32 startup_mode,
    struct recovered_startup_status_helper_18a10 *out)
{
    u32 status = hardware_status & 0xffU;

    if (status == 0xffU) {
        out->mode_byte = 2U;
        out->state_flag = 1U;
    } else if (status == 1U) {
        out->mode_byte = 1U;
        out->state_flag = 0U;
    } else {
        out->mode_byte = 3U;
        out->state_flag = 0U;
    }
    out->status_service_result = status_service_result;
    out->status_address = 0x001d00028U;
    out->state_address = 0x005770b1U;
    out->flag_address = 0x00503a08U;
    out->status_service_call = 0x000c5870U;
    out->state_service_call = 0x00018ab0U;
    out->loop_first_index = 0U;
    out->loop_last_index = 0x77U;
    out->service_gate_open =
        status_service_result == 0U && startup_mode != 5U ? 1U : 0U;
    /* r4 starts at zero and cmpible r4,0x77 keeps the body through 0x77. */
    out->state_service_calls = out->service_gate_open != 0U ? 120U : 0U;
}
