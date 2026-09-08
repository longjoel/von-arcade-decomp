/* Bounded object-record dispatch plan recovered from i960 0x2b430-0x2b4fc. */

typedef unsigned int u32;

enum recovered_object_dispatch_route {
    RECOVERED_OBJECT_DISPATCH_NONE = 0U,
    RECOVERED_OBJECT_DISPATCH_RELEASE = 1U,
    RECOVERED_OBJECT_DISPATCH_TABLE = 2U
};

struct recovered_object_dispatch_plan {
    u32 object_address;
    u32 record_count;
    u32 slot_address;
    u32 slot_left;
    u32 slot_right;
    enum recovered_object_dispatch_route route;
    u32 dispatch_index;
    u32 dispatch_target_address;
    u32 dispatch_count;
    u32 count_address;
};

/* The caller supplies live record/table words; this recovers their routing. */
void recovered_geometry_object_dispatch_plan(
    u32 object_index, u32 record_count, u32 record_field,
    u32 slot_left, u32 slot_right, u32 dispatch_index,
    struct recovered_object_dispatch_plan *plan)
{
    plan->object_address = 0x0051c5b0U + object_index * 0x54U;
    plan->record_count = record_count;
    plan->slot_address = 0x0051bb30U + record_field * 0x54U;
    plan->slot_left = slot_left;
    plan->slot_right = slot_right;
    plan->dispatch_index = dispatch_index;
    plan->dispatch_target_address = 0U;
    plan->count_address = plan->slot_address;
    plan->dispatch_count = 0U;

    if (record_count == 0U) {
        plan->route = RECOVERED_OBJECT_DISPATCH_NONE;
        return;
    }
    /* cmpibl g5,g4: the table path is selected only when left < right. */
    if (slot_left < slot_right) {
        plan->route = RECOVERED_OBJECT_DISPATCH_TABLE;
        plan->dispatch_target_address = 0x0002b420U + dispatch_index * 4U;
    } else {
        plan->route = RECOVERED_OBJECT_DISPATCH_RELEASE;
        plan->dispatch_target_address = 0x0006fd50U;
    }
    plan->dispatch_count = record_count;
}
