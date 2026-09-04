/* Exact bounded slice of the original i960 record-pool service at 0x3f4e8. */
typedef unsigned int u32;
typedef unsigned short u16;

struct recovered_status_record_3f4e8 {
    u32 selector;       /* record +0x00, seeded with 10 */
    u32 table_halfword; /* record +0x02, table[10] */
    u32 helper_value;   /* record +0x04, g14 after the service clears it */
    u32 caller_field;   /* record +0x06, caller g1 (halfword store) */
    u32 caller_value;   /* record +0x08, caller g0 */
};

/*
 * The original scans the 0x51ad10 pool in 0x24-byte increments.  ldis makes
 * the status halfword signed and cmpibg 0,status selects a negative (bit-15)
 * slot.  The routine then seeds selector 10 and performs the 0x3eca0 lookup.
 * Its continuation/helper effects are represented by the pure output fields.
 * Returns the selected slot, or 23 when all bounded slots are unavailable.
 */
u32 recovered_status_record_seed_3f4e8(const u16 status_words[23],
                                       const u16 table_words[65536],
                                       u32 caller_field,
                                       u32 caller_value,
                                       struct recovered_status_record_3f4e8 *out)
{
    u32 slot;

    for (slot = 0U; slot < 23U; ++slot) {
        if ((status_words[slot] & 0x8000U) != 0U) {
            out->selector = 10U;
            out->table_halfword = table_words[10U];
            out->helper_value = 0U;
            out->caller_field = caller_field & 0xffffU;
            out->caller_value = caller_value;
            return slot;
        }
    }
    return 23U;
}
