/* Bounded entry-prefix model for the object state machine at 0x32810. */

typedef unsigned int u32;

struct recovered_geometry_object_state_prefix_plan {
    u32 fifo_address;
    u32 object_source_pointer_offset;
    u32 source_pointer_fields[2];
    u32 object_copy_destinations[2];
    u32 packet_selectors[2];
    u32 packet_selector_count;
    u32 first_response_destination;
    u32 difference_response_destination;
    u32 state_field_offset;
    u32 dispatch_table_address;
    u32 dispatch_target[14];
    u32 dispatch_target_count;
};

void recovered_geometry_object_state_prefix_plan(
    struct recovered_geometry_object_state_prefix_plan *plan)
{
    static const u32 targets[14] = {
        0x000329c4U, 0x000329a0U, 0x00032a88U, 0x00032af4U,
        0x00032b20U, 0x00032b7cU, 0x00032bc0U, 0x00032c1cU,
        0x00032cfcU, 0x00032dccU, 0x00032e40U, 0x00032e74U,
        0x00032ea4U, 0x00032fd0U
    };
    u32 index;

    plan->fifo_address = 0x00884000U;
    plan->object_source_pointer_offset = 0x74U;
    plan->source_pointer_fields[0] = 0x08U;
    plan->source_pointer_fields[1] = 0x10U;
    plan->object_copy_destinations[0] = 0xa4U;
    plan->object_copy_destinations[1] = 0xa8U;
    plan->packet_selectors[0] = 31U;
    plan->packet_selectors[1] = 10U;
    plan->packet_selector_count = 2U;
    plan->first_response_destination = 0x7cU;
    plan->difference_response_destination = 0x84U;
    plan->state_field_offset = 0x1b2U;
    plan->dispatch_table_address = 0x00032968U;
    plan->dispatch_target_count = 14U;
    for (index = 0U; index < plan->dispatch_target_count; ++index)
        plan->dispatch_target[index] = targets[index];
}

/* The assembly masks the state selector to a 16-bit value before dispatch. */
u32 recovered_geometry_object_state_selector(u32 state_word)
{
    return (state_word << 16) >> 16;
}

/* Packet 31 publishes the device response at object offset 0x7c. */
u32 recovered_geometry_object_state_first_response(u32 response)
{
    return response;
}

/* Packet 10 publishes the following response as a signed halfword. */
u32 recovered_geometry_object_state_difference_response(u32 response)
{
    return (response << 16) >> 16;
}
