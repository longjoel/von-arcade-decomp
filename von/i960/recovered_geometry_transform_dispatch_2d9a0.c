/* Bounded model of the geometry transform route at i960 0x2d9a0. */

typedef unsigned int u32;

struct recovered_geometry_transform_plan {
    u32 profile_helper;
    u32 service_helper;
    u32 fifo_address;
    u32 packet_selectors[10];
    u32 packet_selector_count;
    u32 state_address[7];
    u32 state_store_width[7];
    u32 state_write_count;
    u32 continuation;
};

/* The packet selectors and fixed addresses are literal assembly operands. */
void recovered_geometry_transform_dispatch_plan(
    struct recovered_geometry_transform_plan *plan)
{
    static const u32 selectors[10] = { 8U, 16U, 10U, 31U, 29U,
                                       30U, 10U, 20U, 21U, 18U };
    static const u32 state[7] = { 0x0051aad0U, 0x0051aad2U,
                                  0x0051aad4U, 0x0051aad8U,
                                  0x0051aadcU, 0x0051aae0U,
                                  0x0051aae4U };
    static const u32 widths[7] = { 2U, 2U, 2U, 4U, 4U, 4U, 4U };
    u32 index;

    plan->profile_helper = 0x000295d0U;
    plan->service_helper = 0x0002a990U;
    plan->fifo_address = 0x00884000U;
    plan->packet_selector_count = 10U;
    for (index = 0U; index < plan->packet_selector_count; ++index)
        plan->packet_selectors[index] = selectors[index];
    plan->state_write_count = 7U;
    for (index = 0U; index < plan->state_write_count; ++index)
    {
        plan->state_address[index] = state[index];
        plan->state_store_width[index] = widths[index];
    }
    plan->continuation = 0x0002dc40U;
}

/* The two response post-processors are pure and safe to exercise in tests. */
u32 recovered_geometry_transform_low_halfword(u32 response)
{
    return (response << 16) >> 16;
}

u32 recovered_geometry_transform_toggle_sign_bit(u32 value)
{
    return value ^ 0x80000000U;
}

/* 0x51aad2 and 0x51aad4 are halfword stores of the zeroed g14 register. */
void recovered_geometry_transform_state_values(
    u32 adjusted_response, u32 derived_r8, u32 derived_g13,
    u32 derived_g2, u32 derived_g6, u32 values[6])
{
    values[0] = adjusted_response;
    values[1] = 0U;
    values[2] = 0U;
    values[3] = derived_r8;
    values[4] = derived_g13;
    values[5] = derived_g2;
    (void)derived_g6;
}

/* The final derived g6 is stored separately at 0x51aae4. */
u32 recovered_geometry_transform_final_state_value(u32 derived_g6)
{
    return derived_g6;
}
