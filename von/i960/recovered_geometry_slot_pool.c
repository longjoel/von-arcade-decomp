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
