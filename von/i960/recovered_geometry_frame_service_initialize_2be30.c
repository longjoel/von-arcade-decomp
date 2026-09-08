/* Frame-service initializer and dispatch plan recovered from 0x2be30. */

typedef unsigned int u32;

struct recovered_frame_service_initialize_plan {
    u32 profile_helper;
    u32 fifo_prefix[2];
    u32 clear_address[2];
    u32 service_helper;
    u32 service_arg0;
    u32 service_arg1;
    u32 old_counter;
    u32 next_counter;
    u32 counter_reset;
    u32 phase_clear;
    u32 phase_before;
    u32 phase_after;
    u32 dispatch_index;
    u32 dispatch_table_address;
    u32 dispatch_target;
};

static u32 recovered_frame_service_target(u32 index)
{
    static const u32 targets[12] = {
        0x0002c118U, 0x0002c244U, 0x0002cb28U, 0x0002cf80U,
        0x0002cb28U, 0x0002cf80U, 0x0002d3d8U, 0x0002d4e4U,
        0x0002c360U, 0x0002c730U, 0x0002c92cU, 0x0002bf14U
    };

    return targets[index % 12U];
}

void recovered_geometry_frame_service_initialize_plan(
    u32 counter, u32 phase, struct recovered_frame_service_initialize_plan *plan)
{
    plan->profile_helper = 0x000295d0U;
    plan->fifo_prefix[0] = 8U;
    plan->fifo_prefix[1] = 16U;
    plan->clear_address[0] = 0x0050427aU;
    plan->clear_address[1] = 0x00503c7aU;
    plan->service_helper = 0x0002a990U;
    plan->service_arg0 = 0x0000d000U;
    plan->service_arg1 = 0U;
    plan->old_counter = counter;
    plan->next_counter = counter + 1U;
    plan->counter_reset = plan->next_counter > 0xb4U ? 1U : 0U;
    if (plan->counter_reset)
        plan->next_counter = 0U;
    plan->phase_clear = plan->counter_reset;
    plan->phase_before = phase;
    plan->phase_after = plan->counter_reset ? phase + 1U : phase;
    plan->dispatch_index = plan->phase_after % 12U;
    plan->dispatch_table_address = 0x0002bee4U;
    plan->dispatch_target = recovered_frame_service_target(
        plan->dispatch_index);
}
