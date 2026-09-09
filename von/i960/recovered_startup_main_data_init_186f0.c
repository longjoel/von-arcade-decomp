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
    u32 store_count;
    u32 store_addresses[13];
    u32 store_values[13];
    u32 call_count;
    u32 call_targets[3];
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
    {
        u32 i = 0U;
        out->store_addresses[i] = 0x5039f8U;
        out->store_values[i++] = 0U;
        out->store_addresses[i] = 0x504c84U;
        out->store_values[i++] = 0U;
        out->store_addresses[i] = 0x5024d4U;
        out->store_values[i++] = 0U;
        out->store_addresses[i] = 0x503a00U;
        out->store_values[i++] = 0U;
        out->store_addresses[i] = 0x5039f4U;
        out->store_values[i++] = 0U;
        out->store_addresses[i] = 0x5039f0U;
        out->store_values[i++] = 0U;
        out->store_addresses[i] = 0x503aacU;
        out->store_values[i++] = 0U;
        out->store_addresses[i] = 0x503a7cU;
        out->store_values[i++] = 0U;
        out->store_addresses[i] = 0x5770f0U;
        out->store_values[i++] = 0U;
        out->store_addresses[i] = 0x504c88U;
        out->store_values[i++] = 1U;
        out->store_addresses[i] = 0x503ab4U;
        out->store_values[i++] = 0x64U;
        out->store_addresses[i] = 0x503ab8U;
        out->store_values[i++] = 0x258U;
        out->store_addresses[i] = 0x504d10U;
        out->store_values[i++] = 0xffffffffU;
        out->store_count = i;
    }
    out->call_targets[0] = 0x186c0U;
    out->call_targets[1] = 0x18960U;
    out->call_targets[2] = 0x18a10U;
    out->call_count = 3U;
}
