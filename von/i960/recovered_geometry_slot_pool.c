/* Bounded slot-cursor primitives used by the geometry setup at 0x6fa40/0x6fb10. */
typedef unsigned int u32;

u32 recovered_geometry_pool64_acquire(const u32 *slots, u32 count, u32 *new_count)
{
    if (count > 63U) {
        *new_count = count;
        return 0xffffffffU;
    }
    count++;
    *new_count = count;
    return slots[count];
}

u32 recovered_geometry_pool64_release(u32 *slots, u32 count, u32 value, u32 *new_count)
{
    count--;
    slots[count] = value;
    *new_count = count;
    return 1U;
}

/*
 * The 0x6f9e0 reset clears the 64-entry free-slot array and one associated
 * field for each 0x54-byte record before zeroing the pool cursor.  The
 * per-record field is passed as a compact 64-element view of those strided
 * stores, keeping the mapped record layout outside this pure helper.
 */
void recovered_geometry_pool64_reset(u32 *slots, u32 *record_fields,
                                     u32 *count)
{
    u32 index;

    for (index = 0U; index < 64U; ++index) {
        slots[index] = 0U;
        record_fields[index] = 0U;
    }
    *count = 0U;
}

u32 recovered_geometry_pool32_acquire(const u32 *slots, u32 count, u32 *new_count)
{
    if (count > 31U) {
        *new_count = count;
        return 0xffffffffU;
    }
    count++;
    *new_count = count;
    return slots[count];
}

u32 recovered_geometry_pool32_release(u32 *slots, u32 count, u32 value, u32 *new_count)
{
    count--;
    slots[count] = value;
    *new_count = count;
    return 1U;
}

/* The 0x6fad0 reset leaf clears the 32-entry release pool and its cursor. */
void recovered_geometry_pool32_reset(u32 *slots, u32 *count)
{
    u32 index;

    for (index = 0U; index < 32U; ++index)
        slots[index] = 0U;
    *count = 0U;
}
