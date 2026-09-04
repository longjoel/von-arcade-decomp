/* Exact bounded slice of the original i960 routine at 0x3eeb0. */
typedef unsigned int u32;
typedef unsigned short u16;

/*
 * The routine seeds the first active record with selector 17 and three
 * readbacks from the 0x884000 device register.  The device write/read and
 * the 0xf5058 bookkeeping call are intentionally represented as inputs;
 * this contract covers only the record writes surrounding those boundaries.
 */
struct recovered_status_record_reset_3eeb0 {
    u32 selector;       /* record +0x00, caller g1 (halfword store) */
    u32 table_halfword; /* record +0x02 */
    u32 helper_value;   /* record +0x04, caller g14 */
    u32 caller_byte;    /* record +0x06, caller g0 (halfword store) */
    u32 readback8;      /* record +0x08, first device read */
    u32 readbackc;      /* record +0x0c, second device read */
    u32 readback10;     /* record +0x10, third device read */
    u32 zero14;         /* record +0x14 */
    u32 zero18;         /* record +0x18 */
    u32 zero1c;         /* record +0x1c */
    u32 arg0;           /* record +0x20, caller g0 */
};

/* Returns the selected slot, or 23 when the bounded scan found none. */
u32 recovered_status_record_reset_3eeb0(
    const u16 status_words[23], const u16 table_words[65536],
    u32 caller_value, u32 selector, u32 helper_value,
    const u32 device_readbacks[3],
    struct recovered_status_record_reset_3eeb0 *out)
{
    u32 slot;

    for (slot = 0U; slot < 23U; ++slot) {
        if ((status_words[slot] & 0x8000U) != 0U) {
            out->selector = selector & 0xffffU;
            out->table_halfword = table_words[selector & 0xffffU];
            out->helper_value = helper_value;
            out->caller_byte = caller_value & 0xffffU;
            out->readback8 = device_readbacks[0];
            out->readbackc = device_readbacks[1];
            out->readback10 = device_readbacks[2];
            out->zero14 = 0U;
            out->zero18 = 0U;
            out->zero1c = 0U;
            out->arg0 = caller_value;
            return slot;
        }
    }
    return 23U;
}
