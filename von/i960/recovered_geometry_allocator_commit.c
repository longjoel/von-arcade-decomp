/* Deterministic bookkeeping tail recovered from i960 0x6fd1c-0x6fd4c. */
typedef unsigned int u32;

void recovered_geometry_allocator_commit(u32 allocated_slot,
                                         u32 source_count,
                                         u32 current_head,
                                         u32 next_head_word,
                                         u32 *source_record_link,
                                         u32 *new_source_count,
                                         u32 *new_head,
                                         u32 *available_count)
{
    *source_record_link = allocated_slot;
    *new_source_count = source_count + 1U;
    *new_head = current_head + 0x30U;
    *available_count = 0U - next_head_word;
}
