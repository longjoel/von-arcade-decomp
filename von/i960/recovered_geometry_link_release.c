/* Association repair plan recovered from i960 0x6fd50-0x6fe6c. */
typedef unsigned int u32;

struct recovered_geometry_link_update {
    u32 target_kind; /* 0 = side table, 1 = referenced 0x54-byte record */
    u32 target_slot;
    u32 target_offset;
    u32 value;
};

/*
 * link14/link18 are the source record's fields at offsets 0x14 and 0x18.
 * The firmware uses 999 as the no-record sentinel. The two side-table bases
 * are represented by target_kind/target_offset rather than host addresses.
 */
void recovered_geometry_link_release_plan(u32 source_slot,
                                           u32 link14,
                                           u32 link18,
                                           u32 reference_count,
                                           struct recovered_geometry_link_update updates[2],
                                           u32 *new_reference_count)
{
    if (link14 == 999U) {
        updates[0].target_kind = 0U;
        updates[0].target_offset = 0x5c8U;
        updates[0].target_slot = source_slot;
    } else {
        updates[0].target_kind = 1U;
        updates[0].target_offset = 0x18U;
        updates[0].target_slot = link14;
    }
    updates[0].value = link18;

    if (link18 == 999U) {
        updates[1].target_kind = 0U;
        updates[1].target_offset = 0x5c4U;
        updates[1].target_slot = source_slot;
    } else {
        updates[1].target_kind = 1U;
        updates[1].target_offset = 0x14U;
        updates[1].target_slot = link18;
    }
    updates[1].value = link14;
    *new_reference_count = reference_count - 1U;
}
