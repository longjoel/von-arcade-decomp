/*
 * Exact bounded slice of the original i960 routine at 0x3ecd0.
 *
 * The routine scans the 23 records rooted at 0x51ad10 (stride 0x24) for
 * status bit 15, then initializes the first matching record.  The caller's
 * service/helper call is deliberately outside this contract; the resulting
 * value is supplied as helper_value.
 */
typedef unsigned int u32;
typedef unsigned short u16;

struct recovered_status_record_3ecd0 {
    u32 selector;       /* record +0x00, caller g4 (r5) */
    u32 table_halfword; /* record +0x02 */
    u32 helper_value;   /* record +0x04, caller g14 */
    u32 caller_byte;    /* record +0x06, stib g0 */
    u32 arg0;           /* record +0x08 */
    u32 arg1;           /* record +0x0c */
    u32 arg2;           /* record +0x10 */
    u32 zero14;         /* record +0x14 */
    u32 zero18;         /* record +0x18 */
    u32 zero1c;         /* record +0x1c */
    u32 arg3;           /* record +0x20 */
};

/* Returns the selected slot, or 23 when the original bounded scan failed. */
u32 recovered_status_record_init_3ecd0(const u16 status_words[23],
                                       const u16 table_words[65536],
                                       u32 selector,
                                       u32 arg0, u32 arg1, u32 arg2,
                                       u32 arg3, u32 helper_value,
                                       struct recovered_status_record_3ecd0 *out)
{
    u32 slot;

    for (slot = 0U; slot < 23U; ++slot) {
        if ((status_words[slot] & 0x8000U) != 0U) {
            out->selector = selector;
            out->table_halfword = table_words[selector & 0xffffU];
            out->helper_value = helper_value;
            out->caller_byte = arg0 & 0xffU;
            out->arg0 = arg0;
            out->arg1 = arg1;
            out->arg2 = arg2;
            out->zero14 = 0U;
            out->zero18 = 0U;
            out->zero1c = 0U;
            out->arg3 = arg3;
            return slot;
        }
    }
    return 23U;
}
