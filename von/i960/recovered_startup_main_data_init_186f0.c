/* Deterministic initialization prefix recovered from i960 0x186f0-0x1878c. */
#include <stdint.h>

typedef uint32_t u32;

struct recovered_startup_main_data_init_186f0 {
    u32 stack_counter_seed;
    u32 stack_counter_after_drain;
    u32 startup_state_cleared;
    u32 startup_mode_flag;
    u32 startup_service_counter;
    u32 startup_timeout;
    u32 input_initializer_called;
    u32 system_setup_called;
    u32 hardware_status_called;
};

void recovered_startup_main_data_init_186f0(
    struct recovered_startup_main_data_init_186f0 *out)
{
    /* The cmpdeci loop writes 1 then decrements the same frame word to 0. */
    out->stack_counter_seed = 1U;
    out->stack_counter_after_drain = 0U;
    out->startup_state_cleared = 1U;
    out->startup_mode_flag = 0U;
    out->startup_service_counter = 0U;
    out->startup_timeout = 0x00000258U;
    out->input_initializer_called = 1U;
    out->system_setup_called = 1U;
    out->hardware_status_called = 1U;
}
